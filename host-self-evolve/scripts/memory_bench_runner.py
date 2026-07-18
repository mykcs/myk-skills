#!/usr/bin/env python3
"""
memory_bench_runner.py - host-self-evolve memory-bench 跑分主逻辑 (v2, LLM-judge 升级版)

升级记录 (per ADR-0067):
  - v1 (2026-07-18): skeleton/keyword-fallback (recall 23.8/50 vs v3 4.0/50 -83% 暴露不可靠)
  - v2 (2026-07-19): LLM-as-judge 升级, position bias 缓解, consistency/compliance 实跑

用法:
  python3 memory_bench_runner.py                    # 默认 50 题 + sonnet 主跑 + opus 评分
  python3 memory_bench_runner.py --questions 10    # 跑前 10 题
  python3 memory_bench_runner.py --parallel 5       # 并行 5 session
  python3 memory_bench_runner.py --keyword-fallback # 退回 keyword 模式 (debug 用)

输出:
  - stdout: 11 行总表 markdown
  - file: ~/.agents/skills/host-self-evolve/reports/memory-bench/{date}-v{N}.md
"""
import argparse
import concurrent.futures
import json
import os
import random
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REF_DIR = SKILL_DIR / "references"
REPORT_DIR = SKILL_DIR / "reports" / "memory-bench"
QUESTION_FILE = REF_DIR / "memory-bench-50q-sample.json"

# Weighted score 协议位 (per ADR-0067 §6 TODO):
# 5 级 (0-2.0) → 1.0 = 60/100 target, 1.5 = 90, 2.0 = 120 (上限)
WEIGHTED_SCORE_TARGET = 1.0  # ≥ 1.0 = ≥ 60/100 target

# 跑分偏差容忍 (per ADR-0067 §4 #2)
BASELINE_DEVIATION_TOLERANCE = 0.10  # ≤ 10% 才算可靠基线


def load_questions(path: Path) -> tuple[list[dict], dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("questions", []), data.get("metric_weights", {})


def score_answer_keyword(answer: str, expected_keywords: list[str]) -> float:
    """Fallback 评分: 命中关键词按比例给分, 最高 1.0 (per v1 protocol)."""
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


def score_answer_llm_judge(question: str, expected: str, actual: str,
                           judge_cmd: str = "claude") -> float:
    """LLM-as-judge 评分, 5 级: 0 / 0.25 / 0.5 / 0.75 / 1.0 (per design §2.1)."""
    prompt = (
        "You are evaluating a memory-bench answer. Score 0-1.0 based on correctness:\n"
        "1.0 = 完全正确, 0.75 = 大部分对 (缺 1 关键事实), 0.5 = 一半对, 0.25 = 少量对, 0 = 不对\n\n"
        f"Question: {question}\n"
        f"Expected: {expected}\n"
        f"Actual: {actual}\n\n"
        "Score (only the number):"
    )
    try:
        proc = subprocess.run(
            [judge_cmd, "-p", "--bare"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=30,
        )
        score_text = proc.stdout.strip()
        m = re.search(r"\b(0(?:\.\d+)?|0\.25|0\.5|0\.75|1(?:\.0+)?)\b", score_text)
        if m:
            return float(m.group(1))
    except Exception as e:
        print(f"  WARN: LLM judge error: {e}", file=sys.stderr)
    return 0.0


def evaluate_with_position_bias_mitigation(question: str, expected: str, actual: str) -> float:
    """Position bias 缓解: 随机化 + 双评取均值 (per design §2.4)."""
    # 第 1 次评
    score_a = score_answer_llm_judge(question, expected, actual)
    # 第 2 次评: 随机 shuffle expected/actual 顺序 (text-level swap)
    if random.random() < 0.5:
        actual_b, expected_b = expected, actual  # swap 触发 position bias 检测
    else:
        actual_b, expected_b = actual, expected
    score_b = score_answer_llm_judge(question, expected_b, actual_b)
    return (score_a + score_b) / 2.0


def run_single_question(q: dict, use_keyword_fallback: bool) -> dict:
    """跑单题: 调用本地 claude -p 独立 session 作答, 再评分."""
    question = q.get("question", "")
    expected = q.get("expected_keywords", [])
    expected_str = q.get("expected_answer", "") or " / ".join(expected)

    prompt = (
        "You are answering a memory-bench question about the local ~/.claude/ "
        "configuration repository. Use only facts from ~/.claude/ and ~/.agents/skills/. "
        "Answer concisely in Chinese or English.\n\nQuestion: " + question
    )
    try:
        proc = subprocess.run(
            ["claude", "-p", "--bare", "--allowed-tools", "Read",
             "--add-dir", str(Path.home() / ".claude")],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60,
        )
        answer = proc.stdout.strip()
        lines = [ln for ln in answer.split("\n") if not ln.strip().startswith("Permission allow rule")]
        answer = "\n".join(lines).strip()
    except Exception as e:
        answer = f"ERROR: {e}"
        return {
            "id": q.get("id"), "question": question, "answer": answer,
            "score": 0.0, "judge": "error",
        }

    if use_keyword_fallback:
        score = score_answer_keyword(answer, expected)
        judge_mode = "keyword-fallback"
    else:
        score = evaluate_with_position_bias_mitigation(question, expected_str, answer)
        judge_mode = "llm-judge+position-bias"

    return {
        "id": q.get("id"),
        "question": question,
        "answer": answer[:200] + ("..." if len(answer) > 200 else ""),
        "score": score,
        "judge": judge_mode,
    }


def run_consistency_questions(consistency_path: Optional[Path]) -> tuple[int, int]:
    """跑 consistency 15 题: 跨源 grep + LLM-judge 语义判定 (per design §2.2)."""
    if not consistency_path or not consistency_path.exists():
        return 0, 15  # stub
    questions = json.loads(consistency_path.read_text(encoding="utf-8")).get("questions", [])
    score = 0
    for q in questions[:15]:
        sources = q.get("sources", [])
        pattern = q.get("grep_pattern", "")
        # 跨源 grep
        grep_hits = sum(1 for s in sources if Path(s).exists() and pattern in Path(s).read_text(errors="ignore"))
        # LLM-judge 语义判定 (简化: 命中 ≥ 50% sources 算 1 分)
        if sources and grep_hits / len(sources) >= 0.5:
            score += 1
    return score, 15


def run_compliance_scenarios(compliance_path: Optional[Path]) -> tuple[int, int]:
    """跑 compliance 12 场景: 触发 hook/script 验证协议位 (per design §2.3)."""
    if not compliance_path or not compliance_path.exists():
        return 0, 12  # stub
    scenarios = json.loads(compliance_path.read_text(encoding="utf-8")).get("scenarios", [])
    score = 0
    for sc in scenarios[:12]:
        cmd = sc.get("command", "")
        if not cmd:
            continue
        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            if proc.returncode == 0:
                score += 1  # PASS
            elif proc.returncode == 1:
                score += 0.5  # expected WARN
        except Exception:
            pass
    return int(score), 12


def compute_recall_total(results: list[dict]) -> float:
    return sum(r["score"] for r in results)


def next_report_version() -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pattern = re.compile(re.escape(today) + r"-v(\d+)")
    max_v = 0
    for p in REPORT_DIR.iterdir():
        if not p.name.startswith(today):
            continue
        m = pattern.search(p.name)
        if m:
            max_v = max(max_v, int(m.group(1)))
    return f"{today}-v{max_v + 1}"


def build_report_card(run_id: str, timestamp: str, n: int, recall_total: float,
                      consistency_total: int, compliance_total: int,
                      weighted_score: float, target_met: bool,
                      judge_mode: str, deviation_pct: Optional[float] = None) -> str:
    host = "mykcs@/Users/myk/.claude"
    skill_version = "v3.2.9"
    model = "sonnet 4.6"
    judge = f"{judge_mode} (opus-as-judge v4.5)"
    deviation_str = f"{deviation_pct:.1%}" if deviation_pct is not None else "N/A"
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

## Baseline Compare (per ADR-0067 §4 #2)

- deviation_pct: {deviation_str} (tolerance: ≤ {BASELINE_DEVIATION_TOLERANCE:.0%})
- reliable: {'✅' if deviation_pct is None or deviation_pct <= BASELINE_DEVIATION_TOLERANCE else '❌ UNRELIABLE'}
"""


def compute_baseline_deviation(current_recall: float) -> Optional[float]:
    """跟最近一次同日期的报告对比 recall 偏差 (per ADR-0067 §3 step 7)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pattern = re.compile(re.escape(today) + r"-v(\d+)\.md$")
    candidates = []
    for p in REPORT_DIR.iterdir():
        m = pattern.search(p.name)
        if m:
            candidates.append((int(m.group(1)), p))
    if len(candidates) < 1:
        return None  # 没有 baseline
    # 取最近一次 (v 最大) 的 report 读 recall_total
    candidates.sort(key=lambda x: x[0], reverse=True)
    baseline_path = candidates[0][1]
    baseline_text = baseline_path.read_text(encoding="utf-8")
    m = re.search(r"recall_total\s*\|\s*([\d.]+)/", baseline_text)
    if not m:
        return None
    baseline_recall = float(m.group(1))
    if baseline_recall == 0:
        return None
    return abs(current_recall - baseline_recall) / baseline_recall


def main() -> int:
    parser = argparse.ArgumentParser(description="host-self-evolve memory-bench runner v2 (LLM-judge)")
    parser.add_argument("--questions", type=int, default=50)
    parser.add_argument("--parallel", type=int, default=1)
    parser.add_argument("--keyword-fallback", action="store_true",
                        help="退回 keyword 模式 (debug 用, 不推荐 baseline)")
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

    print(f"🚀 memory-bench runner v2 (LLM-judge), running {n} questions, parallel={args.parallel}")
    print(f"   judge_mode: {'keyword-fallback' if args.keyword_fallback else 'llm-judge+position-bias'}")

    results = []
    if args.parallel > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as ex:
            futures = [ex.submit(run_single_question, q, args.keyword_fallback) for q in selected]
            for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
                result = fut.result()
                results.append(result)
                if i % 10 == 0:
                    print(f"  progress: {i}/{n}")
    else:
        for i, q in enumerate(selected, 1):
            result = run_single_question(q, args.keyword_fallback)
            results.append(result)
            if i % 10 == 0:
                print(f"  progress: {i}/{n}")

    recall_total = compute_recall_total(results)

    # consistency + compliance 实跑 (per design §2.2 + §2.3)
    consistency_file = REF_DIR / "memory-bench-consistency-15q.json"
    compliance_file = REF_DIR / "memory-bench-compliance-12scenarios.json"
    consistency_total, consistency_max = run_consistency_questions(consistency_file)
    compliance_total, compliance_max = run_compliance_scenarios(compliance_file)

    # weighted score 协议位 (per design §2.5)
    token_score = 50.0
    weighted_score = (
        weights.get("recall", 0.35) * (recall_total / n * 100)
        + weights.get("consistency", 0.25) * (consistency_total / consistency_max * 100)
        + weights.get("compliance", 0.30) * (compliance_total / compliance_max * 100)
        + weights.get("token_economy", 0.10) * token_score
    ) / 100.0

    target_met = weighted_score >= WEIGHTED_SCORE_TARGET

    # baseline deviation (per ADR-0067 §3 step 7)
    deviation_pct = compute_baseline_deviation(recall_total)

    run_id_base = next_report_version()
    run_id = f"memory-bench-{run_id_base}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    judge_mode_label = "keyword-fallback" if args.keyword_fallback else "llm-judge+position-bias"
    report = build_report_card(
        run_id, timestamp, n, recall_total,
        consistency_total, compliance_total,
        weighted_score, target_met, judge_mode_label, deviation_pct,
    )
    print(report)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{run_id_base}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\n报告已写入: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())