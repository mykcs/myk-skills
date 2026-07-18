#!/usr/bin/env python3
"""PhD Scout CLI entry point."""
import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from src.orchestrator import Orchestrator
from src.writers.lark_writer import _run_lark_cli

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="PhD Scout - Advisor intelligence gathering")
    parser.add_argument("--mode", choices=["single", "batch", "audit", "refresh"], required=True)
    parser.add_argument("--name", help="Teacher name for single mode")
    parser.add_argument("--university", help="University for single mode")
    parser.add_argument("--school", help="School for single mode")
    parser.add_argument("--input", help="Input JSONL file for batch mode")
    parser.add_argument("--filter-tags", help="Filter tags for audit mode")
    parser.add_argument("--base-id", dest="base_id", help="Base app token")
    parser.add_argument("--table-id", dest="table_id", help="Table ID within the base")
    parser.add_argument("--lark-table", help="Base app token (backward compat alias for --base-id)")
    parser.add_argument("--report", action="store_true", help="Generate execution report")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    return parser.parse_args()


async def run_single(args, orchestrator: Orchestrator):
    """Run single teacher processing."""
    teacher = {
        "name": args.name,
        "university": args.university,
        "school": args.school,
    }
    result = await orchestrator.process_teacher(teacher)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.report:
        save_report(result, args.output_dir)

    return result


async def run_batch(args, orchestrator: Orchestrator):
    """Run batch processing from JSONL file."""
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    teachers = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                teachers.append(json.loads(line))

    logger.info(f"Loaded {len(teachers)} teachers from {input_path}")

    results = []
    for i, teacher in enumerate(teachers, 1):
        logger.info(f"Processing {i}/{len(teachers)}: {teacher.get('name')}")
        try:
            result = await orchestrator.process_teacher(teacher)
            results.append(result)

            # Save individual result
            output_dir = Path(args.output_dir) / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            out_file = output_dir / f"{teacher.get('name')}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Failed to process {teacher.get('name')}: {e}")
            error_dir = Path(args.output_dir) / "errors"
            error_dir.mkdir(parents=True, exist_ok=True)
            error_file = error_dir / f"{teacher.get('name')}.error.json"
            with open(error_file, "w", encoding="utf-8") as f:
                json.dump({"teacher": teacher, "error": str(e)}, f, ensure_ascii=False)

    # Summary
    summary = {
        "total": len(teachers),
        "succeeded": len(results),
        "failed": len(teachers) - len(results),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.report:
        save_batch_report(teachers, results, args.output_dir)

    return results


async def run_audit(args, orchestrator: Orchestrator):
    """Run audit mode: detect schema from target table and emit audit report."""
    report = orchestrator.audit_existing_records()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


async def run_refresh(orchestrator: Orchestrator):
    """
    Refresh mode: read all existing teachers from Feishu table,
    run 5-level fetch for each, update records with new data.
    """
    # Get all teachers from table
    field_map = orchestrator.lark_writer._build_field_map()
    name_field = field_map.get("name", "姓名")

    ok, stdout, stderr = _run_lark_cli([
        "base", "+record-list",
        "--base-token", orchestrator.lark_writer.app_token,
        "--table-id", orchestrator.lark_writer.table_id,
        "--limit", "500"
    ])
    if not ok:
        logger.error(f"Failed to read records: {stderr}")
        print(json.dumps({"status": "error", "message": stderr}))
        return

    resp = json.loads(stdout)
    raw_data = resp.get("data", {})
    fields = raw_data.get("fields", [])
    records = raw_data.get("data", [])
    record_ids = raw_data.get("record_id_list", [])

    # Find name field index
    name_idx = None
    school_idx = None
    for i, f in enumerate(fields):
        if f == name_field:
            name_idx = i
        if f == field_map.get("school", "学院"):
            school_idx = i

    if name_idx is None:
        logger.error(f"Name field '{name_field}' not found in table")
        return

    teachers = []
    for i, row in enumerate(records):
        if not row or len(row) <= name_idx:
            continue
        name = row[name_idx]
        school = row[school_idx] if school_idx is not None and school_idx < len(row) else "软件学院"
        record_id = record_ids[i] if i < len(record_ids) else None
        # Get existing 近3年文章 text for signal fallback
        papers_idx = None
        for fi, f in enumerate(fields):
            if f == field_map.get("papers", "近3年文章"):
                papers_idx = fi
                break
        existing_papers = row[papers_idx] if papers_idx is not None and papers_idx < len(row) else None
        if name:
            teachers.append({
                "name": name,
                "university": "浙大",
                "school": school,
                "_record_id": record_id,
                "_existing_papers": existing_papers,
            })

    logger.info(f"Found {len(teachers)} teachers to refresh")

    results = []
    for i, teacher in enumerate(teachers, 1):
        name = teacher.get("name")
        logger.info(f"[{i}/{len(teachers)}] Refreshing: {name}")
        try:
            result = await orchestrator.process_teacher(teacher)
            results.append(result)
            logger.info(f"  → signal={result.get('signal')}, h_index={result.get('h_index')}")
        except Exception as e:
            logger.error(f"  → Failed: {e}")
            results.append({"name": name, "status": "error", "error": str(e)})

    summary = {
        "total": len(teachers),
        "succeeded": sum(1 for r in results if r.get("status") != "error"),
        "failed": sum(1 for r in results if r.get("status") == "error"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return results


def main():
    args = parse_args()

    orchestrator = Orchestrator()

    if args.mode == "single":
        if not args.name or not args.university:
            logger.error("--name and --university required for single mode")
            sys.exit(1)
        asyncio.run(run_single(args, orchestrator))
    elif args.mode == "batch":
        if not args.input:
            logger.error("--input required for batch mode")
            sys.exit(1)
        asyncio.run(run_batch(args, orchestrator))
    elif args.mode == "audit":
        if args.base_id:
            orchestrator.lark_writer.app_token = args.base_id
            orchestrator.lark_writer._schema_cache = None
        if args.table_id:
            orchestrator.lark_writer.table_id = args.table_id
            orchestrator.lark_writer._schema_cache = None
        asyncio.run(run_audit(args, orchestrator))
    elif args.mode == "refresh":
        if not args.base_id or not args.table_id:
            logger.error("--base-id and --table-id required for refresh mode")
            sys.exit(1)
        orchestrator.lark_writer.app_token = args.base_id
        orchestrator.lark_writer.table_id = args.table_id
        orchestrator.lark_writer._schema_cache = None
        asyncio.run(run_refresh(orchestrator))


if __name__ == "__main__":
    main()
