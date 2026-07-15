"""ntn_client.py — Notion API 调 ntn CLI 共享 client (v4.1+).

替代 paper-into-notion.py / schema.py / verify_all_fields.py 各自硬编码 ntn subprocess.
所有调用走 60s timeout + 3 次 retry + 统一错误处理.

为什么不放每文件复用函数: 3 文件复用逻辑复制 → drift 风险. 抽出公共 client.
"""
from __future__ import annotations

import json
import subprocess


def ntn_call(method: str, path: str, body: dict | None = None, timeout: int = 60) -> dict:
    """调 ntn CLI (per v4.1 实测 Notion API 偶发 30s 卡死, 升级 60s + 3 retry).

    Args:
        method: GET / POST / PATCH
        path: e.g. /v1/data_sources/{id}/query
        body: optional JSON body (POST/PATCH 才有)
        timeout: per-attempt timeout (秒). 90 默认 + retry 3 次最坏总 270s.

    Returns:
        parsed JSON dict (空响应返 {})

    Raises:
        RuntimeError: 3 次重试都失败
        json.JSONDecodeError: stdout 不是 JSON
    """
    cmd = ["ntn", "api", "--method", method, path]
    if body is not None:
        cmd += ["-d", json.dumps(body, ensure_ascii=False)]
    last_err = None
    for attempt in range(3):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if r.returncode != 0:
                last_err = r.stderr[:200] or f"exit {r.returncode}"
                continue
            return json.loads(r.stdout) if r.stdout.strip() else {}
        except subprocess.TimeoutExpired as e:
            last_err = f"timeout after {timeout}s: {e}"
            continue
        except json.JSONDecodeError as e:
            last_err = f"JSON decode fail: stdout={r.stdout[:200] if 'r' in dir() else 'n/a'}, err={e}"
            continue
    raise RuntimeError(f"ntn api {method} {path} 失败 (3 次重试): {last_err}")
