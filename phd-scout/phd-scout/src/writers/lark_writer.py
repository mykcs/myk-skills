"""Lark/Feishu writer for PhD Scout via lark-cli with schema auto-detection."""
import json
import logging
import subprocess
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_APP_TOKEN = "Cr5bbmbCmaC67IsQ5yUcjN7cnEe"
DEFAULT_TABLE_ID = "tbllrwGBjIH8r8xp"

# Semantic field mapping: standard_field → list of possible field name patterns (prioritized)
SEMANTIC_MAPPING = {
    "name":          ["姓名", "name", "导师", "老师", "老师姓名"],
    "university":    ["大学", "university", "学校", "高校"],
    "school":        ["学院", "school", "系", "department", "学部"],
    "raw_title":     ["职称", "title", "职务", "职级", "学术头衔"],
    "research_tags": ["研究方向", "方向", "tags", "research", "研究领域"],
    "contact_status": ["联系状态", "状态", "contact", "联系", "联系进度"],
    "priority":      ["推荐优先级", "优先级", "priority", "优先度"],
    "direction_score": ["方向匹配度", "匹配度", "方向分数", "方向度"],
    "email":         ["邮箱", "email", "mail", "电子邮件"],
    "homepage":      ["主页", "url", "link", "website", "个人主页", "主页链接"],
    "notes":         ["备注", "notes", "note", "备注信息"],
    "students_info": ["学生情况", "学生", "学生信息", "学生去向"],
    "papers":        ["近3年文章", "论文", "papers", "发表论文", "近三年论文"],
    "h_index":       ["h指数", "h-index", "H指数", "学术能力"],
    "signal":        ["危险信号", "信号", "signal", "状态信号"],
    "h_index":       ["h指数", "h-index", "H指数", "学术能力", "h_index"],
}


def _run_lark_cli(args: list) -> tuple:
    """Run lark-cli command, return (ok, stdout, stderr)."""
    cmd = ["lark-cli", "--as", "user"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr


class LarkWriter:
    """
    Writes teacher data to Feishu/Bitable via lark-cli --as user.
    Auto-detects target table schema and dynamically maps fields.
    """

    def __init__(self, app_token: Optional[str] = None, table_id: Optional[str] = None):
        self.app_token = app_token or os.environ.get("LARK_APP_TOKEN", DEFAULT_APP_TOKEN)
        self.table_id = table_id or os.environ.get("LARK_TABLE_ID", DEFAULT_TABLE_ID)
        self._schema_cache: Optional[dict] = None  # {field_name: field_id}

    # ─── Schema Detection ────────────────────────────────────────────────

    def _detect_schema(self) -> dict[str, str]:
        """
        Detect target table's field structure.
        Returns: {field_name: field_id}
        """
        if self._schema_cache:
            return self._schema_cache

        ok, stdout, stderr = _run_lark_cli([
            "base", "+field-list",
            "--base-token", self.app_token,
            "--table-id", self.table_id,
        ])
        if not ok:
            logger.warning(f"Schema detect failed: {stderr}")
            return {}

        try:
            resp = json.loads(stdout)
            fields = resp.get("data", {}).get("fields", [])
            self._schema_cache = {f["name"]: f["id"] for f in fields}
            logger.info(f"Schema detected: {list(self._schema_cache.keys())}")
            return self._schema_cache
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Parse schema failed: {e}")
            return {}

    def _build_field_map(self) -> dict[str, str]:
        """
        Build standard_field → lark_field_name mapping based on detected schema.
        Returns: {standard_field: lark_field_name}
        """
        schema = self._detect_schema()
        if not schema:
            return {}

        available = set(schema.keys())
        field_map = {}

        for std_field, patterns in SEMANTIC_MAPPING.items():
            # Try patterns in priority order, match if field exists in table
            for pattern in patterns:
                if pattern in available:
                    field_map[std_field] = pattern
                    break

        logger.info(f"Field map built: {field_map}")
        return field_map

    # ─── Record Operations ───────────────────────────────────────────────

    def write_teacher(self, teacher: dict) -> dict:
        """
        Upsert a teacher record. Uses dynamic field mapping.
        """
        name = teacher.get("name", "") or ""
        fields = self._teacher_to_fields(teacher)

        existing = self._find_by_name(name)
        if existing:
            return self._update_record(existing["record_id"], fields)
        else:
            return self._create_record(fields)

    def _find_by_name(self, name: str) -> Optional[dict]:
        """
        Find record by name, using any field that maps to 'name'.
        """
        field_map = self._build_field_map()
        if not field_map.get("name"):
            # Fallback: try common field names
            for candidate in ["姓名", "导师", "name"]:
                existing = self._find_by_field(name, candidate)
                if existing:
                    return existing
            return None
        return self._find_by_field(name, field_map["name"])

    def _find_by_field(self, value: str, field_name: str) -> Optional[dict]:
        """Find record by specific field name and value."""
        ok, stdout, stderr = _run_lark_cli([
            "base", "+record-list",
            "--base-token", self.app_token,
            "--table-id", self.table_id,
            "--field-id", field_name,
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
            # Find the index of the name field
            name_idx = None
            for i, f in enumerate(fields):
                if f == field_name:
                    name_idx = i
                    break
            if name_idx is None:
                return None
            for i, row in enumerate(records):
                if row and len(row) > name_idx and row[name_idx] == value:
                    return {
                        "record_id": record_ids[i] if i < len(record_ids) else None,
                        "fields": dict(zip(fields, row))
                    }
            return None
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Parse search result failed: {e}")
            return None

    def _create_record(self, fields: dict) -> dict:
        """Create new record."""
        field_json = json.dumps(fields, ensure_ascii=False)
        ok, stdout, stderr = _run_lark_cli([
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
        """Update existing record."""
        field_json = json.dumps(fields, ensure_ascii=False)
        ok, stdout, stderr = _run_lark_cli([
            "base", "+record-upsert",
            "--base-token", self.app_token,
            "--table-id", self.table_id,
            "--record-id", record_id,
            "--json", field_json
        ])
        if not ok:
            logger.warning(f"Update failed, trying create: {stderr}")
            return self._create_record(fields)
        return {"status": "success", "record_id": record_id}

    # ─── Field Mapping ───────────────────────────────────────────────────

    def _teacher_to_fields(self, teacher: dict) -> dict:
        """
        Convert teacher dict to Feishu fields using dynamic field mapping.
        Unmapped fields are logged but not written.
        """
        field_map = self._build_field_map()
        schema = self._detect_schema()
        unmapped = []

        lark_fields = {}

        # Direct field mappings (only write if teacher actually has the value;
        # don't overwrite with university name when email is missing)
        direct_map = {
            "name":       teacher.get("name"),
            "school":     teacher.get("school"),
            "raw_title":  teacher.get("raw_title"),
            "homepage":   teacher.get("homepage"),
        }
        # Only map university/email if teacher has an explicit value (not auto-filled)
        if teacher.get("university") and teacher.get("university") not in ("浙大", "浙江大学"):
            direct_map["university"] = teacher.get("university")
        if teacher.get("email"):
            direct_map["email"] = teacher.get("email")

        for std_field, value in direct_map.items():
            if value and std_field in field_map:
                lark_field_name = field_map[std_field]
                lark_fields[lark_field_name] = value

        # research_tags → 研究方向 (select, list)
        if teacher.get("research_tags") and "research_tags" in field_map:
            lark_fields[field_map["research_tags"]] = teacher["research_tags"]

        # contact_status → 联系状态 (select)
        if teacher.get("contact_status") and "contact_status" in field_map:
            lark_fields[field_map["contact_status"]] = teacher["contact_status"]

        # priority → 推荐优先级 (select)
        if teacher.get("priority") and "priority" in field_map:
            lark_fields[field_map["priority"]] = teacher["priority"]

        # direction_score → 方向匹配度 (number) — only write if explicitly set (> 0)
        # Don't overwrite with 0 when fetchers failed and score defaulted
        ds = teacher.get("direction_score")
        if ds is not None and ds > 0 and "direction_score" in field_map:
            lark_fields[field_map["direction_score"]] = ds

        # notes → 备注 (text) — append signal to existing notes, don't overwrite
        signal = teacher.get("signal", "")
        if signal and "notes" in field_map:
            existing_note = teacher.get("notes", "")
            emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(signal, signal)
            note = f"{emoji} {signal}"
            if existing_note and existing_note != note:
                note = f"{existing_note} | {note}"
            lark_fields[field_map["notes"]] = note

        # tags → 课题组 (text)
        tags = teacher.get("tags", [])
        if tags and "tags" in field_map:
            lark_fields[field_map["tags"]] = " ".join(tags)
        elif tags and "notes" in field_map:
            existing = lark_fields.get(field_map["notes"], "")
            lark_fields[field_map["notes"]] = f"{existing} {' '.join(tags)}".strip()

        # recent_papers → 近3年文章 (text)
        papers = teacher.get("recent_papers") or teacher.get("papers", [])
        if papers and "papers" in field_map:
            paper_text = self._format_papers(papers)
            lark_fields[field_map["papers"]] = paper_text

        # h-index
        h_index = teacher.get("h_index")
        if h_index is not None and "h_index" in field_map:
            lark_fields[field_map["h_index"]] = h_index

        # signal → 危险信号 (select) — only write if not unknown; map en→zh
        SIGNAL_MAP = {"green": "绿灯", "yellow": "黄灯", "red": "红灯"}
        signal = teacher.get("signal", "")
        if signal and signal not in ("", "unknown") and "signal" in field_map:
            lark_fields[field_map["signal"]] = SIGNAL_MAP.get(signal, signal)

        # Build unmapped report
        for std_field in SEMANTIC_MAPPING:
            if std_field in teacher and teacher[std_field] and std_field not in field_map:
                unmapped.append(std_field)

        if unmapped:
            logger.info(f"Unmapped fields (no target column found): {unmapped}")
            lark_fields["_unmapped"] = unmapped

        return lark_fields

    def _format_papers(self, papers: list) -> str:
        """Format paper list as readable text."""
        lines = []
        for p in papers[:20]:  # cap at 20
            title = p.get("title", "未知标题")
            year = p.get("year", "?")
            venue = p.get("venue", "?")
            citations = p.get("citations")
            line = f"- {title} ({year}) [{venue}]"
            if citations:
                line += f" @cite={citations}"
            lines.append(line)
        return "\n".join(lines)

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

    def truncate_if_needed(self, value: str, max_len: int = 10000) -> str:
        """Truncate field value if too long."""
        if len(value) <= max_len:
            return value
        return value[:max_len] + " [截断]"