"""Rank standardization for Chinese academic titles."""
import json
import re
from pathlib import Path
from typing import Optional


class RankStandardizer:
    """
    Standardizes Chinese academic/administrative/talent ranks.

    Three-track system:
    - Academic: AP → Associate → Full → Chair → Academician
    - Admin: 系主任 → 副院长 → 院长 → 校级
    - Talent: 无 → 四青 → 杰青/长江 → 更高
    """

    def __init__(self, mapping_path: str = None):
        if mapping_path is None:
            skill_dir = Path(__file__).resolve().parent.parent.parent
            mapping_path = skill_dir / "config" / "rank_mapping.json"
            mapping_path = str(mapping_path)
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.mapping = json.load(f)

        self.academic = self.mapping.get("academic", {})
        self.admin = self.mapping.get("admin", {})
        self.talent = self.mapping.get("talent", {})

    def standardize(self, raw_title: str) -> dict:
        """
        Parse raw title and return standardized ranks.

        Args:
            raw_title: Original title string from university website

        Returns:
            dict with keys: academic, admin, talent (each a list of standardized ranks)
        """
        result = {
            "academic": [],
            "admin": [],
            "talent": [],
            "raw": raw_title
        }

        if not raw_title:
            return result

        text = raw_title.lower()

        # Match academic ranks
        for pattern, rank in self.academic.items():
            if pattern.lower() in text:
                if rank not in result["academic"]:
                    result["academic"].append(rank)

        # Match admin ranks
        for pattern, rank in self.admin.items():
            if pattern.lower() in text:
                if rank not in result["admin"]:
                    result["admin"].append(rank)

        # Match talent ranks
        for pattern, rank in self.talent.items():
            if pattern.lower() in text:
                if rank not in result["talent"]:
                    result["talent"].append(rank)

        return result

    def to_display_string(self, raw_title: str) -> str:
        """Convert raw title to a compact display string."""
        std = self.standardize(raw_title)
        parts = std["academic"] + std["admin"] + std["talent"]
        return " / ".join(parts) if parts else raw_title

    def is_empty(self, raw_title: str) -> bool:
        """Check if raw title has no recognizable ranks."""
        std = self.standardize(raw_title)
        return not (std["academic"] or std["admin"] or std["talent"])
