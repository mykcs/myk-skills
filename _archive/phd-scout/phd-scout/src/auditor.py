"""Auditor for PhD Scout - merge strategy for existing teachers."""
from typing import Optional
from datetime import datetime


class Auditor:
    """
    Handles audit mode when teacher already exists in Feishu.

    Merge rules:
    - Papers: union + deduplicate
    - h-index: update + append to log
    - Students: merge + deduplicate + update status
    - Danger signal: if green→yellow/red, mark "有更新待审" not auto-update
    - Admin rank changes: auto-update + append to change log
    """

    def audit(self, existing: dict, new: dict) -> dict:
        """
        Audit and merge new data into existing record.

        Args:
            existing: Existing teacher record from Feishu
            new: New teacher data from fetchers

        Returns:
            Merged teacher dict with audit_status set appropriately
        """
        merged = existing.copy()

        # Merge papers (union + dedup by title)
        existing_papers = existing.get("recent_papers", [])
        new_papers = new.get("recent_papers", [])
        merged["recent_papers"] = self._merge_papers(existing_papers, new_papers)

        # Update h-index with log
        new_h_index = new.get("h_index")
        if new_h_index and new_h_index != existing.get("h_index"):
            merged["h_index"] = new_h_index
            log_entry = f"{datetime.now().date()}: {existing.get('h_index')} → {new_h_index}"
            merged["h_index_log"] = existing.get("h_index_log", [])
            merged["h_index_log"].append(log_entry)

        # Merge students
        merged["students"] = self._merge_students(
            existing.get("students", []),
            new.get("students", [])
        )

        # Merge collaborators
        merged["collaborators"] = self._merge_collaborators(
            existing.get("collaborators", []),
            new.get("collaborators", [])
        )

        # Danger signal: only auto-update green→green, otherwise mark pending
        new_signal = new.get("signal")
        old_signal = existing.get("signal")
        if new_signal and new_signal != old_signal:
            if self._is_downgrade(old_signal, new_signal):
                merged["audit_status"] = "有更新待审"
                merged["signal_pending"] = new_signal
            else:
                merged["signal"] = new_signal

        # Admin rank changes: auto-update
        if new.get("standardized_ranks"):
            merged["standardized_ranks"] = new["standardized_ranks"]

        # Research tags: union
        old_tags = set(existing.get("research_tags", []))
        new_tags = set(new.get("research_tags", []))
        merged["research_tags"] = list(old_tags | new_tags)

        # Update metadata
        merged["last_updated"] = datetime.now().isoformat()
        merged["audit_status"] = merged.get("audit_status", "已审计")

        return merged

    def _merge_papers(self, existing: list, new: list) -> list:
        """Merge paper lists, deduplicate by title."""
        titles = {p.get("title") for p in existing}
        merged = list(existing)

        for paper in new:
            title = paper.get("title")
            if title and title not in titles:
                merged.append(paper)
                titles.add(title)

        return merged

    def _merge_students(self, existing: list, new: list) -> list:
        """Merge student lists, update status."""
        student_map = {s.get("name"): s for s in existing}

        for student in new:
            name = student.get("name")
            if name in student_map:
                # Update status if new info is more recent
                existing_student = student_map[name]
                if student.get("status") == "in_progress" and existing_student.get("status") == "unknown":
                    student_map[name] = student
            else:
                student_map[name] = student

        return list(student_map.values())

    def _merge_collaborators(self, existing: list, new: list) -> list:
        """Merge collaborator lists."""
        collab_map = {c.get("name"): c for c in existing}

        for collab in new:
            name = collab.get("name")
            if name in collab_map:
                # Sum paper counts
                old_count = collab_map[name].get("co_paper_count", 0)
                new_count = collab.get("co_paper_count", 0)
                collab_map[name]["co_paper_count"] = old_count + new_count
            else:
                collab_map[name] = collab

        return list(collab_map.values())

    def _is_downgrade(self, old_signal: str, new_signal: str) -> bool:
        """Check if signal change is a downgrade (worse)."""
        order = {"green": 0, "yellow": 1, "red": 2}
        return order.get(new_signal, 0) > order.get(old_signal, 0)
