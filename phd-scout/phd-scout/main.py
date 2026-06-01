#!/usr/bin/env python3
"""PhD Scout CLI entry point."""
import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from src.orchestrator import Orchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="PhD Scout - Advisor intelligence gathering")
    parser.add_argument("--mode", choices=["single", "batch", "audit"], required=True)
    parser.add_argument("--name", help="Teacher name for single mode")
    parser.add_argument("--university", help="University for single mode")
    parser.add_argument("--school", help="School for single mode")
    parser.add_argument("--input", help="Input JSONL file for batch mode")
    parser.add_argument("--filter-tags", help="Filter tags for audit mode")
    parser.add_argument("--lark-table", help="Feishu table ID")
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
    """Run audit mode for existing teachers."""
    logger.info("Audit mode - fetching existing records from Feishu")
    logger.info("Note: Audit requires feishu-agent skill or direct API access")
    print(json.dumps({
        "status": "not_implemented",
        "message": "Audit mode requires feishu-agent skill integration"
    }, ensure_ascii=False, indent=2))


def save_report(result: dict, output_dir: str):
    """Save execution report."""
    output_path = Path(output_dir) / "reports"
    output_path.mkdir(parents=True, exist_ok=True)
    name = result.get("name", "unknown")
    report_file = output_path / f"{name}_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(result.get("report", result), f, ensure_ascii=False, indent=2)


def save_batch_report(teachers: list, results: list, output_dir: str):
    """Save batch execution summary."""
    output_path = Path(output_dir) / "reports"
    output_path.mkdir(parents=True, exist_ok=True)
    summary_file = output_path / "batch_summary.json"
    summary = {
        "total": len(teachers),
        "succeeded": len(results),
        "failed": len(teachers) - len(results),
        "results": [
            {
                "name": r.get("name"),
                "signal": r.get("signal"),
                "confidence": r.get("confidence"),
            }
            for r in results
        ]
    }
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def main():
    args = parse_args()

    # Extract Lark credentials from args or environment
    lark_table = args.lark_table

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
        asyncio.run(run_audit(args, orchestrator))


if __name__ == "__main__":
    main()
