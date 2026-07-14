"""schema.py — Notion data source schema 解析 + 字段名映射 (v4 SSOT).

替代 v3.x 11 shell 散落的字段名硬编码 + introspect.py 24h cache.
每次 query page 反推字段名 (5min TTL cache, 短到 schema drift 自动恢复).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FieldMap:
    """db 真实字段名映射 (从 query page 反推).

    v3.x 硬编码 + introspect cache 是 drift 主因 — 这里从 page.properties 拿真名,
    schema 改了自动 fallback.
    """

    title: str
    status: str
    modal: str
    link: str | None
    highlights: str
    keyword: str | None
    org: str | None
    knowledge_growth: str | None

    @classmethod
    def from_page(cls, page: dict[str, Any]) -> "FieldMap":
        """从 query db 拿一个 page, 反推字段名 (type → name)."""
        props = page.get("properties", {})

        def first_of_type(t: str) -> str | None:
            for name, p in props.items():
                if p.get("type") == t:
                    return name
            return None

        def select_with_keyword(*keywords: str) -> str | None:
            """select 字段含关键词优先 (区分 平台形式 vs 旧 模态类型)."""
            for name, p in props.items():
                if p.get("type") == "select":
                    if any(k in name for k in keywords):
                        return name
            return first_of_type("select")

        def multi_select_with_keyword(*keywords: str) -> str | None:
            for name, p in props.items():
                if p.get("type") == "multi_select":
                    if any(k in name for k in keywords):
                        return name
            return first_of_type("multi_select")

        return cls(
            title=first_of_type("title") or "页面",
            status=first_of_type("status") or "状态",
            # 平台形式 / 平台 / 模态类型 — 优先含"平台"的 select (drift-resistant)
            modal=select_with_keyword("平台", "模态") or "平台形式",
            link=first_of_type("url"),
            highlights=first_of_type("rich_text") or "亮点",
            # 关键词 / 知识点 / 标签 — multi_select 含"关键词"优先
            keyword=multi_select_with_keyword("关键词", "标签", "知识点"),
            org=multi_select_with_keyword("机构"),
            # 知识等级形态 — multi_select 含"知识"或"形态"优先
            knowledge_growth=multi_select_with_keyword("知识", "形态"),
        )


class SchemaCache:
    """5min TTL schema cache (替代 v3.x 24h introspect cache).

    设计 rationale:
    - 短 TTL 让 schema drift 自动恢复 (不需要手动 rm .introspect-cache.json)
    - cache miss → ntn api POST query db 拿 1 个 page → 反推字段名
    - cache hit → 直接用, 不调 ntn
    """

    def __init__(self, cache_dir: Path, ttl_seconds: int = 300):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_or_fetch(self, ds_id: str, ntn_query_func) -> FieldMap:
        cache_file = self.cache_dir / f"schema-{ds_id}.json"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < self.ttl_seconds:
                return self._from_cache_file(cache_file)
        # cache miss → query db 拿 1 个 page 反推
        page = ntn_query_func(ds_id)
        field_map = FieldMap.from_page(page)
        self._write_cache(cache_file, field_map)
        return field_map

    def _from_cache_file(self, f: Path) -> FieldMap:
        d = json.loads(f.read_text())
        return FieldMap(**d)

    def _write_cache(self, f: Path, fm: FieldMap) -> None:
        f.write_text(json.dumps(fm.__dict__, ensure_ascii=False, indent=2))


def ntn_query_latest_page(ds_id: str) -> dict[str, Any]:
    """POST /v1/data_sources/{id}/query 拿最新 1 个 page (调 ntn CLI)."""
    cmd = [
        "ntn", "api", "--method", "POST",
        f"/v1/data_sources/{ds_id}/query",
        "-d",
        json.dumps({
            "page_size": 1,
            "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}],
        }),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    r.check_returncode()
    data = json.loads(r.stdout)
    results = data.get("results", [])
    if not results:
        raise RuntimeError(f"db {ds_id} empty, 不能反推字段名")
    return results[0]


if __name__ == "__main__":
    # 单测入口: python schema.py <DS_ID>
    if len(sys.argv) < 2:
        print("用法: python schema.py <DS_ID>", file=sys.stderr)
        sys.exit(1)
    cache = SchemaCache(Path("cache/"))
    fm = cache.get_or_fetch(sys.argv[1], ntn_query_latest_page)
    print(json.dumps(fm.__dict__, ensure_ascii=False, indent=2))