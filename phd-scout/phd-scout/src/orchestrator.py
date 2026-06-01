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
from src.writers.lark_writer import LarkWriter
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
        """Determine danger signal based on fetch results and paper activity."""
        levels_failed = report.get("levels_failed", {})

        # 🔴 Red: all L1-L4 failed
        l1_failed = "L1" in levels_failed
        l2_failed = "L2" in levels_failed
        l3_failed = "L3" in levels_failed
        l4_failed = "L4" in levels_failed

        if l1_failed and l2_failed and l3_failed and l4_failed:
            return "red"

        # 🟡 Yellow: L1 success but no recent papers
        if not l1_failed:
            papers = data.get("papers", [])
            recent_papers = [p for p in papers if p.get("year", 0) >= datetime.now().year - 3]
            if len(recent_papers) == 0:
                return "yellow"

            direction_score = data.get("direction_score", 0)
            if direction_score == 0:
                return "yellow"

        # 🟢 Green: everything else
        return "green"

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

    def _build_abandon_reason(self, report: dict) -> str:
        """Build abandonment log from failed levels."""
        lines = []
        for level, reason in report.get("levels_failed", {}).items():
            lines.append(f"{level}: {reason}")
        return "\n".join(lines)
