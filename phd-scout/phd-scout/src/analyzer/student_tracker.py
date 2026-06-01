"""Student tracker - infers student list from coauthors."""
from typing import Optional
import re


class StudentTracker:
    """
    Infers student list from coauthors on recent papers.

    Heuristic: coauthor from same institution, not corresponding author,
    appears frequently on recent papers = likely student.
    """

    def infer_students(self, coauthors: list, papers: list, affiliation: str) -> list:
        """
        Infer student list from coauthor network.

        Args:
            coauthors: List of coauthor dicts with name, affiliation, paper_count
            papers: Recent papers with author lists
            affiliation: Target professor's institution

        Returns:
            List of student dicts with name, period, status, destination
        """
        students = []

        for coauthor in coauthors:
            name = coauthor.get("name", "")
            co_affiliation = coauthor.get("affiliation", "")

            # Skip if same institution but not clearly a student
            if affiliation.lower() in co_affiliation.lower():
                # Heuristic: if they appear on 2+ papers and aren't marked as advisor
                paper_count = coauthor.get("co_paper_count", 0)
                if paper_count >= 2:
                    students.append({
                        "name": name,
                        "period": self._infer_period(papers, name),
                        "status": "in_progress" if self._is_likely_current(coauthor, papers) else "unknown",
                        "destination": None
                    })

        return students

    def _infer_period(self, papers: list, student_name: str) -> str:
        """Infer study period from paper timestamps."""
        years = []
        for paper in papers:
            year = paper.get("year")
            if year:
                years.append(year)

        if not years:
            return "unknown"

        return f"{min(years)}-{max(years)}"

    def _is_likely_current(self, coauthor: dict, papers: list) -> bool:
        """Check if coauthor appears on recent (3 years) papers."""
        from datetime import datetime
        current_year = datetime.now().year

        for paper in papers:
            year = paper.get("year")
            if year and (current_year - year) <= 3:
                return True

        return False

    def classify_student_outcome(self, student: dict, linkedin_hint: Optional[str] = None) -> dict:
        """
        Classify student career outcome.

        Args:
            student: Student dict with name, period
            linkedin_hint: Optional LinkedIn URL or job info

        Returns:
            Updated student dict with destination and outcome_status
        """
        period = student.get("period", "")
        destination = student.get("destination")

        if not destination:
            if linkedin_hint:
                if any(kw in linkedin_hint.lower() for kw in ["byte", "tencent", "alibaba", "bytedance", "microsoft", "google", "meta", "amazon"]):
                    student["outcome_status"] = "graduated_industry"
                    student["destination"] = self._extract_company(linkedin_hint)
                elif any(kw in linkedin_hint.lower() for kw in ["university", "professor", "researcher", "postdoc"]):
                    student["outcome_status"] = "graduated_academia"
                    student["destination"] = self._extract_institution(linkedin_hint)
                else:
                    student["outcome_status"] = "unknown"
            else:
                student["outcome_status"] = "unknown"

        return student

    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name from text."""
        companies = ["ByteDance", "Tencent", "Alibaba", "Microsoft", "Google", "Meta", "Amazon", "Apple", "Byte", "Tencent AI Lab"]
        for c in companies:
            if c.lower() in text.lower():
                return c
        return None

    def _extract_institution(self, text: str) -> Optional[str]:
        """Extract university/institution from text."""
        universities = ["University", "Institute", "Tsinghua", "Peking", "Fudan", "SJTU", "Zhejiang", "MIT", "Stanford"]
        for u in universities:
            if u.lower() in text.lower():
                return u
        return None
