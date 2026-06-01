"""Lark/Feishu writer for PhD Scout via lark-cli."""
import json
import logging
import subprocess
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Default credentials from feishu-shenbo-tracker project
DEFAULT_APP_TOKEN = "Cr5bbmbCmaC67IsQ5yUcjN7cnEe"
DEFAULT_TABLE_ID = "tbllrwGBjIH8r8xp"


class LarkWriter:
    """
    Writes teacher data to Feishu/Bitable via lark-cli --as user.
    Uses user OAuth credentials (lark-cli auth login), not bot token.
    """

    def __init__(self, app_token: Optional[str] = None, table_id: Optional[str] = None):
        self.app_token = app_token or os.environ.get("LARK_APP_TOKEN", DEFAULT_APP_TOKEN)
        self.table_id = table_id or os.environ.get("LARK_TABLE_ID", DEFAULT_TABLE_ID)

    def write_teacher(self, teacher: dict) -> dict:
        """
        Upsert a teacher record to Feishu via lark-cli.

        Uses Upsert-First strategy: search by name, update if exists, create if not.
        """
        name = teacher.get("name", "")
        fields = self._teacher_to_fields(teacher)

        # Try to find existing record
        existing = self._find_by_name(name)
        if existing:
            return self._update_record(existing["record_id"], fields)
        else:
            return self._create_record(fields)

    def _run_lark_cli(self, args: list) -> tuple:
        """Run lark-cli command, return (ok, stdout, stderr)."""
        cmd = ["lark-cli", "--as", "user"] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr

    def _find_by_name(self, name: str) -> Optional[dict]:
        """Find record by teacher name (uses 导师 field).

        lark-cli 1.0.19 does not support --filter; fetch records and filter in Python.
        Response is array-of-arrays format: data.data[i] = [field0, field1, ...]
        with parallel arrays: record_id_list[i] and fields[i].
        """
        ok, stdout, stderr = self._run_lark_cli([
            "base", "+record-list",
            "--base-token", self.app_token,
            "--table-id", self.table_id,
            "--field-id", "导师",
            "--limit", "100"
        ])
        if not ok:
            logger.warning(f"Search failed: {stderr}")
            return None
        try:
            resp = json.loads(stdout)
            data = resp.get("data", {})
            fields = data.get("fields", [])
            records = data.get("data", [])
            record_ids = data.get("record_id_list", [])
            if not fields or not records:
                return None
            teacher_idx = None
            for i, row in enumerate(records):
                if row and row[0] == name:
                    teacher_idx = i
                    break
            if teacher_idx is None:
                return None
            return {
                "record_id": record_ids[teacher_idx] if teacher_idx < len(record_ids) else None,
                "fields": dict(zip(fields, records[teacher_idx]))
            }
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Parse search result failed: {e}")
            return None

    def _create_record(self, fields: dict) -> dict:
        """Create new record via upsert."""
        field_json = json.dumps(fields, ensure_ascii=False)
        ok, stdout, stderr = self._run_lark_cli([
            "base", "+record-upsert",
            "--base-token", self.app_token,
            "--table-id", self.table_id,
            "--json", field_json
        ])
        if not ok:
            logger.error(f"Create failed: {stderr}")
            return {"status": "error", "message": stderr}
        try:
            data = json.loads(stdout)
            record_id = data.get("data", {}).get("record", {}).get("record_id")
            return {"status": "success", "record_id": record_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _update_record(self, record_id: str, fields: dict) -> dict:
        """Update existing record via upsert with record-id."""
        field_json = json.dumps(fields, ensure_ascii=False)
        ok, stdout, stderr = self._run_lark_cli([
            "base", "+record-upsert",
            "--base-token", self.app_token,
            "--table-id", self.table_id,
            "--record-id", record_id,
            "--json", field_json
        ])
        if not ok:
            # If update fails (e.g. field doesn't exist in schema), try create
            logger.warning(f"Update failed, trying create: {stderr}")
            return self._create_record(fields)
        return {"status": "success", "record_id": record_id}

    def _get_access_token(self) -> str:
        """Get Feishu access token via direct API (fallback)."""
        import requests
        app_id = os.environ.get("LARK_APP_ID", "cli_a9523fc7d0389cb2")
        app_secret = os.environ.get("LARK_APP_SECRET", "SE63CtGI8QY7YzNAejhOZft2GGY6xPc4")
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        response = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
        data = response.json()
        if data.get("code") != 0:
            raise Exception(f"Failed to get access token: {data.get('msg')}")
        return data.get("tenant_access_token", "")

    def _teacher_to_fields(self, teacher: dict) -> dict:
        """Convert teacher dict to Feishu fields (existing shenbo-tracker schema)."""
        fields = {}

        # Map to existing table fields
        field_mapping = {
            "name": "导师",
            "university": "大学",
            "school": "学院",
            "raw_title": "行政能力",  # raw title goes to 行政能力
        }

        for key, field_name in field_mapping.items():
            if key in teacher and teacher[key] is not None:
                fields[field_name] = teacher[key]

        # Research direction → 研究方向 select
        if teacher.get("research_tags"):
            fields["研究方向"] = teacher["research_tags"]

        # Students info → 学生情况
        if teacher.get("students"):
            fields["学生情况"] = self._format_students(teacher["students"])

        # Student destinations → 学生去向
        students = teacher.get("students", [])
        if students:
            dests = [s.get("destination", "未知") for s in students if s.get("destination")]
            if dests:
                fields["学生去向"] = ", ".join(dests)

        # h-index as text in 学术能力
        h_index = teacher.get("h_index")
        if h_index is not None:
            fields["学术能力"] = f"h-index: {h_index}"

        # Signal in notes
        signal = teacher.get("signal", "")
        if signal:
            emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(signal, signal)
            fields["备注"] = f"{emoji} {signal}"

        # Tags in 课题组
        tags = teacher.get("tags", [])
        if tags:
            fields["课题组"] = " ".join(tags)

        return fields

    def _format_students(self, students: list) -> str:
        """Format student list as Markdown."""
        lines = []
        for s in students:
            name = s.get("name", "未知")
            period = s.get("period", "")
            status = s.get("status", "")
            dest = s.get("destination", "")
            lines.append(f"- {name} ({period}) [{status}]" + (f" → {dest}" if dest else ""))
        return "\n".join(lines)

    def truncate_if_needed(self, value: str, field_name: str, max_len: int = 10000) -> str:
        """Truncate field value if too long, mark as truncated."""
        if len(value) <= max_len:
            return value
        return value[:max_len] + " [截断]"
