"""Orchestrator for PhD Scout - main execution loop."""
import asyncio
import json
import logging
import traceback
from datetime import datetime
from typing import Optional

from src.fetchers.university import UniversityFetcher
from src.fetchers.scholar import ScholarFetcher
from src.fetchers.semantic_scholar import SemanticScholarFetcher
from src.fetchers.dblp import DBLPFetcher
from src.fetchers.social import SocialFetcher
from src.analyzer.direction import DirectionAnalyzer
from src.analyzer.rank_standardize import RankStandardizer
from src.analyzer.student_tracker import StudentTracker
from src.writers.lark_writer import LarkWriter, _run_lark_cli, SEMANTIC_MAPPING
from src.auditor import Auditor

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main orchestrator for PhD Scout.

    Reads teacher from queue → executes 5-level fetch → analyzes →
    determines danger signal → writes to Feishu.
    """

    def __init__(
        self,
        lark_app_token: Optional[str] = None,
        lark_table_id: Optional[str] = None,
    ):
        self.fetcher_l1 = UniversityFetcher()
        self.fetcher_l2 = ScholarFetcher()
        self.fetcher_l3 = SemanticScholarFetcher()
        self.fetcher_l4 = DBLPFetcher()
        self.fetcher_l5 = SocialFetcher()

        self.direction_analyzer = DirectionAnalyzer()
        self.rank_standardizer = RankStandardizer()
        self.student_tracker = StudentTracker()
        # app_token = base (app) token, table_id = table id
        self.lark_writer = LarkWriter(lark_app_token, lark_table_id)
        self.auditor = Auditor()

    async def process_teacher(self, teacher: dict) -> dict:
        """
        Process a single teacher through the full pipeline.

        Args:
            teacher: dict with name, university, school, raw_title (optional)

        Returns:
            dict with execution report
        """
        name = teacher.get("name")
        university = teacher.get("university")
        school = teacher.get("school")
        raw_title = teacher.get("raw_title", "")

        report = {
            "name": name,
            "university": university,
            "school": school,
            "started_at": datetime.now().isoformat(),
            "levels_attempted": [],
            "levels_failed": {},
            "signal": "unknown",
            "status": "pending",
        }

        data = {
            "name": name,
            "university": university,
            "school": school,
            "raw_title": raw_title,
            "papers": [],
            "coauthors": [],
            "h_index": None,
            "standardized_ranks": [],
            "research_tags": [],
            "students": [],
            "collaborators": [],
        }

        # Carry over existing papers from table (refresh mode)
        if teacher.get("_existing_papers"):
            data["_existing_papers"] = teacher["_existing_papers"]

        # L1: University website
        try:
            result = await self.fetcher_l1.fetch(name, university, school)
            if result.get("success"):
                data.update(result)
                report["levels_attempted"].append("L1")
            else:
                report["levels_failed"]["L1"] = result.get("error", "unknown")
        except Exception as e:
            report["levels_failed"]["L1"] = str(e)[:200]

        # L2: Google Scholar (non-blocking failure)
        try:
            result = await self.fetcher_l2.fetch(name, university)
            if result.get("success"):
                data.update(result)
                report["levels_attempted"].append("L2")
            else:
                report["levels_failed"]["L2"] = result.get("error", "unknown")
                logger.warning(f"L2 failed for {name}: {result.get('error')}")
        except Exception as e:
            report["levels_failed"]["L2"] = str(e)[:200]
            logger.warning(f"L2 exception for {name}: {e}")

        # L3: Semantic Scholar API
        try:
            result = await self.fetcher_l3.fetch(name, university)
            if result.get("success"):
                data.update(result)
                report["levels_attempted"].append("L3")
            else:
                report["levels_failed"]["L3"] = result.get("error", "unknown")
        except Exception as e:
            report["levels_failed"]["L3"] = str(e)[:200]

        # L4: DBLP
        try:
            result = await self.fetcher_l4.fetch(name, university)
            if result.get("success"):
                data.update(result)
                report["levels_attempted"].append("L4")
            else:
                report["levels_failed"]["L4"] = result.get("error", "unknown")
        except Exception as e:
            report["levels_failed"]["L4"] = str(e)[:200]

        # L5: Social platforms (manual mode)
        data["social_needs_manual"] = True
        report["levels_attempted"].append("L5")
        report["levels_failed"]["L5"] = "[需手动补充]"

        # Standardize ranks
        if raw_title:
            std = self.rank_standardizer.standardize(raw_title)
            data["standardized_ranks"] = (
                std.get("academic", []) +
                std.get("admin", []) +
                std.get("talent", [])
            )

        # Analyze direction
        papers = data.get("papers", [])
        direction_result = self.direction_analyzer.analyze_papers(papers)
        data["research_tags"] = direction_result.get("all_matched_keywords", [])
        data["direction_score"] = direction_result.get("direction_score", 0.0)

        # Process papers for Kimi review if needed
        borderline = direction_result.get("needs_kimi_review", [])
        if borderline:
            for item in borderline:
                title = item.get("title", "")
                paper = item.get("paper", {})
                abstract = paper.get("abstract")
                kimi_result = await self.direction_analyzer.analyze_with_kimi(title, abstract)
                if kimi_result.get("is_relevant"):
                    data["papers"].append({**paper, "direction_score": kimi_result.get("confidence", 0.0)})

        # Determine danger signal
        data["signal"] = self._determine_signal(report, data)
        report["signal"] = data["signal"]

        # Compute confidence and fullness scores
        data["confidence"] = self._compute_confidence(report)
        data["fullness_score"] = self._compute_fullness(data)

        # Build tags
        data["tags"] = self._build_tags(data, report)

        # Add metadata
        data["abandon_reason"] = self._build_abandon_reason(report) if data["signal"] == "red" else None
        data["last_updated"] = datetime.now().isoformat()

        # Write to Feishu
        try:
            write_result = self.lark_writer.write_teacher(data)
            report["write_status"] = write_result.get("status")
            report["status"] = "success" if write_result.get("status") == "success" else "partial"
        except Exception as e:
            error_msg = str(e)
            if "FATAL" in error_msg:
                report["status"] = "fatal"
                report["fatal_error"] = error_msg
                logger.error(f"FATAL error writing to Lark: {error_msg}")
            else:
                report["status"] = "write_error"
                report["write_error"] = error_msg

        report["completed_at"] = datetime.now().isoformat()
        data["report"] = report

        return data

    def _determine_signal(self, report: dict, data: dict) -> str:
        """
        Determine danger signal based on fetch results and paper activity.
        Falls back to existing table data (近3年文章 text field) when fetchers fail.
        """
        levels_failed = report.get("levels_failed", {})
        l3_failed = "L3" in levels_failed
        l4_failed = "L4" in levels_failed

        # Has papers from successful fetch?
        papers = data.get("papers", [])
        recent_papers = [p for p in papers if p.get("year", 0) >= datetime.now().year - 3]

        # Has existing table papers (近3年文章 text field)?
        existing_papers_text = data.get("_existing_papers")

        # 🟢 Green if: fetchers got papers OR we have existing table data
        if recent_papers or (existing_papers_text and not (l3_failed and l4_failed)):
            return "green"

        # 🟡 Yellow: fetchers succeeded but no recent papers
        if not l3_failed and not recent_papers:
            return "yellow"

        # 🔴 Red: L3 & L4 both failed AND no existing papers to fall back on
        if l3_failed and l4_failed and not existing_papers_text:
            return "red"

        return "green"  # Safe default: avoid red when there's any data

    def _compute_confidence(self, report: dict) -> int:
        """Compute 1-5 confidence score."""
        levels_succeeded = len(report.get("levels_attempted", []))
        if levels_succeeded >= 4:
            return 5
        elif levels_succeeded == 3:
            return 4
        elif levels_succeeded == 2:
            return 3
        elif levels_succeeded == 1:
            return 2
        return 1

    def _compute_fullness(self, data: dict) -> int:
        """Compute 1-5 information completeness score."""
        score = 0
        if data.get("h_index") is not None:
            score += 1
        if len(data.get("papers", [])) > 0:
            score += 1
        if len(data.get("students", [])) > 0:
            score += 1
        if len(data.get("collaborators", [])) > 0:
            score += 1
        if data.get("standardized_ranks"):
            score += 1
        return min(score, 5)

    def _build_tags(self, data: dict, report: dict) -> list:
        """Build tag list based on data characteristics."""
        tags = []

        if data.get("signal") == "green":
            tags.append("#信息完整")
        elif data.get("signal") == "yellow":
            tags.append("#需手动补充")

        if data.get("direction_score", 0) > 0.5:
            tags.append("#方向精准")

        if len(data.get("students", [])) > 3:
            tags.append("#学生强")

        admin_ranks = data.get("standardized_ranks", [])
        if any(r in admin_ranks for r in ["院长", "副院长", "系主任"]):
            tags.append("#大行政")

        if len(report.get("levels_attempted", [])) >= 4:
            tags.append("#高活跃")

        return tags

    def audit_existing_records(self) -> dict:
        """
        Audit mode: read all existing records from the target Feishu table,
        detect schema, and emit an audit report (no re-fetch, no writes).
        Used when target table schema doesn't match standard phd-scout schema.
        """
        schema = self.lark_writer._detect_schema()
        field_map = self.lark_writer._build_field_map()

        # Read all records
        ok, stdout, stderr = _run_lark_cli([
            "base", "+record-list",
            "--base-token", self.lark_writer.app_token,
            "--table-id", self.lark_writer.table_id,
            "--limit", "500"
        ])
        if not ok:
            return {"status": "error", "message": stderr}

        resp = json.loads(stdout)
        raw_data = resp.get("data", {})
        fields = raw_data.get("fields", [])
        records = raw_data.get("data", [])
        record_ids = raw_data.get("record_id_list", [])

        report = {
            "status": "audit_complete",
            "schema_detected": schema,
            "field_map": field_map,
            "unmapped_fields": [],
            "records_audited": 0,
            "record_reports": []
        }

        # Build reverse map: lark_field_name → standard_field
        reverse_map = {v: k for k, v in field_map.items()}

        # Check which standard fields have no target column
        for std_field in SEMANTIC_MAPPING:
            if std_field not in field_map:
                report["unmapped_fields"].append(std_field)

        for i, row in enumerate(records):
            if not row:
                continue
            record_id = record_ids[i] if i < len(record_ids) else None
            field_dict = dict(zip(fields, row))

            name = field_dict.get(field_map.get("name", ""), "")
            school = field_dict.get(field_map.get("school", ""), "")
            university = field_dict.get(field_map.get("university", ""), "浙大")

            rec_report = {
                "name": name,
                "record_id": record_id,
                "university": university,
                "school": school,
            }

            # Map standard fields from this record
            mapped = {}
            for std_f, lark_f in field_map.items():
                val = field_dict.get(lark_f)
                if val is not None:
                    mapped[std_f] = val

            rec_report["mapped_fields"] = list(mapped.keys())
            rec_report["signal"] = "unknown"  # No external fetch, can't determine

            report["record_reports"].append(rec_report)
            report["records_audited"] += 1

        return report

    def _build_abandon_reason(self, report: dict) -> str:
        """Build abandonment log from failed levels."""
        lines = []
        for level, reason in report.get("levels_failed", {}).items():
            lines.append(f"{level}: {reason}")
        return "\n".join(lines)
