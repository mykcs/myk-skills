"""judge.py — 5 字段 LLM judge (v4 替代 v3.x 5 个 bash judge script).

5 字段: highlights / keyword / org / knowledge_growth / modal
prompt 走 prompts/*.md TOML-driven (改 prompt 不碰代码, 跟 v2.6.49 description split 协议协同).

mmx v4 输出格式 (Anthropic-style):
  {"content": [{"type": "thinking", "thinking": "..."}, {"type": "text", "text": "..."}]}
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JudgeResult:
    highlights: str
    keyword: list[str]
    org: list[str]
    knowledge_growth: list[str]


def mmx_call(prompt: str, mmx_args: list[str]) -> str:
    """调 mmx CLI 跑 LLM judge (per v2.7 mmx 三件套: --non-interactive --output json).

    反模式 #30 (v3.x 永久失效): --quiet 不带 --output json 走 TTY chat mode, json.loads 失败.

    Returns: LLM 输出的 text block 内容 (跳过 thinking block).
    """
    cmd = ["mmx"] + mmx_args + ["--message", prompt]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"mmx 失败 (exit {r.returncode}): {r.stderr[:200]}")
    try:
        data = json.loads(r.stdout)
        content = data.get("content", [])
        for block in reversed(content):
            if block.get("type") == "text":
                return block.get("text", "").strip()
        # fallback: OpenAI choices 格式
        return data["choices"][0]["message"]["content"].strip()
    except (json.JSONDecodeError, KeyError) as e:
        raise RuntimeError(f"mmx 输出解析失败: stdout={r.stdout[:300]}, err={e}")


def _load_prompt(prompts_dir: Path, name: str) -> str:
    f = prompts_dir / f"{name}.md"
    if not f.exists():
        raise FileNotFoundError(f"prompt 不存在: {f}")
    return f.read_text().strip()


def judge_5_fields(
    abstract: str,
    authors: str,
    prompts_dir: Path,
    mmx_args: list[str],
) -> JudgeResult:
    """5 字段 LLM judge (单次 mmx call 输出 JSON 解析).

    v3.x 拆 5 次 mmx call (highlights/knowledge/education/institutions/growth),
    慢 + 5 处 fallback silent. v4 = 1 次 mmx call + JSON 解析, 快 + 1 处错误处理.
    """
    system_prompt = _load_prompt(prompts_dir, "judge-5-fields")
    user_prompt = f"abstract: {abstract}\nauthors: {authors}"
    full_prompt = f"{system_prompt}\n\n{user_prompt}\n\n输出 JSON 格式:\n{{\n  \"highlights\": \"...\",\n  \"keyword\": [\"...\"],\n  \"org\": [\"...\"],\n  \"knowledge_growth\": [\"...\"]\n}}"

    raw = mmx_call(full_prompt, mmx_args)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    data = json.loads(raw)
    return JudgeResult(
        highlights=data.get("highlights", "").strip(),
        keyword=data.get("keyword", []),
        org=data.get("org", []),
        knowledge_growth=data.get("knowledge_growth", []),
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python judge.py <abstract> <authors>", file=sys.stderr)
        sys.exit(1)
    prompts_dir = Path(__file__).parent / "prompts"
    mmx_args = ["text", "chat", "--non-interactive", "--output", "json", "--max-tokens", "4096"]
    result = judge_5_fields(sys.argv[1], sys.argv[2], prompts_dir, mmx_args)
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))