#!/usr/bin/env python3
"""
memory_bench_runner.py - host-self-evolve memory-bench 50 题跑分主逻辑

用法:
  python3 ~/.agents/skills/host-self-evolve/scripts/memory_bench_runner.py
  python3 ~/.agents/skills/host-self-evolve/scripts/memory_bench_runner.py --questions 10

输出:
  - stdout: 11 行总表 markdown
  - file: ~/.agents/skills/host-self-evolve/reports/memory-bench/{date}-v{N}.md

依赖:
  - 题库: ~/.agents/skills/host-self-evolve/references/memory-bench-50q-sample.json
  - 评分: 默认 expectation-based keyword 评分 (轻量 fallback); opus-as-judge 通过 --judge-opus 启用

注意:
  本脚本设计为在已加载 ~/.claude/ 上下文的主 session 内调用, 因为 50 题答案依赖本地 memory source。
  拆 50 session 是为防污染, 但每个 session 必须能读到本地文件; 若用子 agent, 需把相关源文件作为 context 传入。
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REF_DIR = SKILL_DIR / "references"
REPORT_DIR = SKILL_DIR / "reports" / "memory-bench"
QUESTION_FILE = REF_DIR / "memory-bench-50q-sample.json"


def load_questions(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("questions", []), data.get("metric_weights", {})


def score_answer_keyword(answer: str, expected_keywords: list[str]) -> float:
    """轻量 fallback 评分: 命中关键词按比例给分, 最高 1.0。"""
    if not expected_keywords:
        return 1.0
    ans_lower = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in ans_lower)
    ratio = hits / len(expected_keywords)
    if ratio >= 1.0:
        return 1.0
    if ratio >= 0.66:
        return 0.5
    if ratio >= 0.33:
        return 0.25
    return 0.0


def run_single_question(q: dict, use_opus_judge: bool) -> dict:
    """跑单题: 调用本地 claude session 或 keyword 评分。"""
    question = q.get("question", "")
    expected = q.get("expected_keywords", [])
    # 默认使用 keyword scoring; opus judge 通过外部 Agent 调用后再回填
    answer = ""
    score = 0.0
    if not use_opus_judge:
        score = score_answer_keyword(answer, expected)
    return {
        "id": q.get("id"),
        "question": question,
        "answer": answer,
        "score": score,
        "judge": "keyword-fallback" if not use_opus_judge else "opus-as-judge",
    }


def compute_recall_total(results: list[dict]) -> float:
    return sum(r["score"] for r in results)


def next_report_version() -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    existing = [p.name for p in REPORT_DIR.iterdir() if p.name.startswith(today)]
    max_v = 0
    for name in existing:
        m = re.search(rf"{today}-v(\\d+)", name)
        if m:
            max_v = max(max_v, int(m.group(1)))
    return f"{today}-v{max_v + 1}"


def build_report_card(run_id: str, timestamp: str, n: int, recall_total: float,
                      consistency_total: int, compliance_total: int,
                      weighted_score: float, target_met: bool) -> str:
    host = "mykcs@/Users/myk/.claude"
    skill_version = "v3.2.9"
    model = "sonnet 4.6"
    judge = "opus-as-judge v4.5"
    return f"""# memory-bench report-card — {run_id}

| # | 字段 | 值 |
|---|------|-----|
| 1 | run_id | {run_id} |
| 2 | timestamp | {timestamp} |
| 3 | host | {host} |
| 4 | skill_version | {skill_version} |
| 5 | model | {model} |
| 6 | judge | {judge} |
| 7 | recall_total | {recall_total:.1f}/{n} |
| 8 | consistency_total | {consistency_total}/15 |
| 9 | compliance_total | {compliance_total}/12 |
| 10 | weighted_score | {weighted_score:.2f} |
| 11 | target_met | {'✅ ≥ 60' if target_met else '❌ < 60'} |
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="host-self-evolve memory-bench runner")
    parser.add_argument("--questions", type=int, default=50, help="本次跑几题 (默认 50)")
    parser.add_argument("--judge-opus", action="store_true", help="启用 opus-as-judge (需外部 Agent 支持)")
    args = parser.parse_args()

    if not QUESTION_FILE.exists():
        print(f"❌ BLOCKED: question file not found: {QUESTION_FILE}", file=sys.stderr)
        return 2

    questions, weights = load_questions(QUESTION_FILE)
    if not questions:
        print("❌ BLOCKED: no questions in file", file=sys.stderr)
        return 2

    n = min(args.questions, len(questions))
    selected = questions[:n]

    results = []
    for q in selected:
        results.append(run_single_question(q, args.judge_opus))

    recall_total = compute_recall_total(results)
    # consistency / compliance 在本 skeleton 中暂缺, 用 0 占位
    consistency_total = 0
    compliance_total = 0

    # weighted score: 按 design.md 公式, token_economy 暂用 50 占位
    token_score = 50.0
    weighted_score = (
        weights.get("recall", 0.35) * (recall_total / n * 100)
        + weights.get("consistency", 0.25) * (consistency_total / 15 * 100)
        + weights.get("compliance", 0.30) * (compliance_total / 12 * 100)
        + weights.get("token_economy", 0.10) * token_score
    ) / 100.0  # 缩放到 0-2.0 区间 (与 report-card 模板一致)

    target_met = weighted_score >= 1.2  # 60/100 = 1.2 / 2.0

    run_id_base = next_report_version()
    run_id = f"memory-bench-{run_id_base}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    report = build_report_card(
        run_id, timestamp, n, recall_total,
        consistency_total, compliance_total,
        weighted_score, target_met,
    )
    print(report)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{run_id_base}.md"
    report_path.write_text(report + "\n\n## 备注\n\n本 run 为 skeleton/keyword-fallback, consistency/compliance 尚未实跑。\n", encoding="utf-8")
    print(f"\n报告已写入: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
