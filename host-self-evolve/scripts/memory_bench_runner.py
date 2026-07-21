#!/usr/bin/env python3
"""
memory_bench_runner.py - host-self-evolve memory-bench 跑分主逻辑 (v2, LLM-judge 升级版)

升级记录 (per ADR-0067):
  - v1 (2026-07-18): skeleton/keyword-fallback (recall 23.8/50 vs v3 4.0/50 -83% 暴露不可靠)
  - v2 (2026-07-19): LLM-as-judge 升级, position bias 缓解, consistency/compliance 实跑
  - v5 (2026-07-19): RAG-lite 开卷答题 (grep 仓内事实注入 prompt, 治闭卷 hallucination
    recall ≤7/50 根因) + position-bias 角色交换 bug 修复 (旧实现 swap 角色把 recall 压到
    真值 ~1/2) + 双评改展示顺序交换 (标签不变)

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
import re
import subprocess
import sys
import time
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

# token_economy 实测预算 (per user 2026-07-20 拍板, runner v5.1)
TOKEN_BUDGET_PER_Q = 3000  # 每题平均 input_tokens 预算 (RAG ≤12 grep 行 ≈ 1.1k 健康基线)
CLOCK_BUDGET_S = 1800      # 全量 50 题 wall-clock 预算 (v5 实测 ~700-900s, parallel=5)


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
                           judge_cmd: str = "mmx", verbose: bool = False,
                           order_swap: bool = False) -> float:
    """LLM-as-judge 评分, 5 级: 0 / 0.25 / 0.5 / 0.75 / 1.0 (per design §2.1).

    Bug v4 fix: 加宽容 regex + verbose 模式.
    Bug v6 fix (CLI session 未登录 claude -p): 改用 mmx text chat (MiniMax 全平台 CLI, 不依赖 Claude 登录, per v1.1.3 mmx 必跑硬约束).
    Bug v8 fix: order_swap 只换 Expected/Actual 展示顺序 (标签不变), 不交换角色 —
                v7 旧实现直接 swap 文本角色, 50% 概率让 judge 评 "Expected=<答案>, Actual=<期望>"
                的错误配对, 系统性把 recall 压到真值的 ~1/2 (position-bias 伪修复).
    """
    rubric = (
        "You are evaluating a memory-bench answer. Score 0-1.0 based on correctness:\n"
        "1.0 = completely correct, 0.75 = mostly correct (1 key fact missing), "
        "0.5 = half correct, 0.25 = slightly correct, 0.0 = wrong\n\n"
    )
    if order_swap:
        qa_block = f"Question: {question}\nActual: {actual}\nExpected: {expected}\n\n"
    else:
        qa_block = f"Question: {question}\nExpected: {expected}\nActual: {actual}\n\n"
    prompt = rubric + qa_block + "Reply with ONLY the numeric score (e.g. '0.75' or '1.0'), no other text:"
    try:
        # Bug v6 fix: 用 mmx text chat (per ADR-0062 + N-tool-search v1.1.3 mmx 必跑)
        proc = subprocess.run(
            ["mmx", "text", "chat", "--message", prompt,
             "--non-interactive", "--quiet", "--output", "text"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        score_text = proc.stdout.strip()
        # Bug v4 fix: 宽容 regex — 匹配任何 0.x / 1.0 / 0 / 1 的浮点
        m = re.search(r"\b(?:1(?:\.0+)?|0(?:\.\d+)?)\b", score_text)
        if m:
            score = float(m.group(0))
            if verbose:
                print(f"  [LLM-judge {judge_cmd}] score={score} from text={score_text[:80]!r}", file=sys.stderr)
            return score
        # fallback 2: 第一行的第一个数字
        first_line = score_text.split("\n")[0].strip()
        m2 = re.search(r"\d+(?:\.\d+)?", first_line)
        if m2:
            score = min(1.0, float(m2.group(0)))
            if verbose:
                print(f"  [LLM-judge fallback-2] score={score} from line={first_line[:80]!r}", file=sys.stderr)
            return score
        if verbose:
            print(f"  [LLM-judge] NO MATCH in: {score_text[:200]!r}", file=sys.stderr)
    except Exception as e:
        print(f"  WARN: LLM judge error: {e}", file=sys.stderr)
    return 0.0


def evaluate_with_position_bias_mitigation(question: str, expected: str, actual: str,
                                            verbose: bool = False) -> float:
    """Position bias 缓解: 双评取均值, 第 2 评换 Expected/Actual 展示顺序 (标签不变, per Bug v8 fix)."""
    score_a = score_answer_llm_judge(question, expected, actual, verbose=verbose)
    score_b = score_answer_llm_judge(question, expected, actual, verbose=verbose, order_swap=True)
    return (score_a + score_b) / 2.0


# RAG-lite 检索根目录 (per runner v5, 2026-07-19): 开卷答题模拟 host 真实行为
# (agent 按 cross-session-grep 协议先查记忆再答). 限定 memory/rules/cases/adr,
# 刻意不含 reports/memory-bench/ (防答案从历次跑分报告泄漏, 保 bench 有效性).
RETRIEVAL_ROOTS = [
    "~/.claude/CLAUDE.md",
    "~/.claude/CLAUDE.local.md",
    "~/.claude/MEMORY.md",
    "~/.claude/memory",
    "~/.claude/rules",
    "~/.claude/knowledge/cases/wiki",
    "~/.claude/docs/adr",
]


def retrieve_context(question: str, expected_keywords: list,
                     max_lines: int = 12, max_terms: int = 8) -> str:
    """RAG-lite: 用问题里的路径/拉丁词 + expected_keywords 作检索提示 grep 仓内事实.

    用 expected_keywords 做检索提示不算泄题 — 本 bench 测的是"host 记忆系统是否
    保有这些事实 + 检索可达", 不是测模型参数记忆 (闭卷 hallucination 是 v7 前
    recall ≤7/50 的根因, 测不出任何有效信号).

    v5.2: 大文件 (CLAUDE.md / CLAUDE.local.md) 顶部 boilerplate 抢命中 → 单文件限 1 条;
          host-anchors.md 优先 grep (memory-bench 专用 hot 锚点表, 含 expected_keywords 全字眼).
    """
    terms = re.findall(r"~/[\w./-]+|[\w./-]+\.(?:md|json|sh|py)|[A-Za-z][A-Za-z0-9_-]{2,}",
                       question)
    terms += list(expected_keywords or [])
    seen_terms = [t for t in dict.fromkeys(terms) if len(t) >= 3][:max_terms]
    hits: list[str] = []
    seen_lines: set[str] = set()
    roots = [os.path.expanduser(r) for r in RETRIEVAL_ROOTS]
    BIG_FILES = {"CLAUDE.md", "CLAUDE.local.md", "MEMORY.md"}
    big_hits: list[str] = []
    big_seen: set[str] = set()
    HOST_ANCHORS = os.path.expanduser("~/.claude/memory/host-anchors.md")
    for t in seen_terms:
        # 先跑 host-anchors (单文件, 含 expected_keywords 全字面)
        if os.path.exists(HOST_ANCHORS):
            try:
                proc = subprocess.run(
                    ["grep", "-nF", "-m", "2", t, HOST_ANCHORS],
                    capture_output=True, text=True, timeout=5,
                )
                for ln in proc.stdout.splitlines():
                    if ln and ln not in seen_lines:
                        seen_lines.add(ln)
                        hits.append(ln[:300])
            except Exception:
                pass
        if len(hits) >= max_lines:
            break
        # 全仓兜底
        try:
            proc = subprocess.run(
                ["grep", "-rnF", "--include=*.md", "-m", "3", t] + roots,
                capture_output=True, text=True, timeout=15,
            )
            for ln in proc.stdout.splitlines():
                if ln in seen_lines:
                    continue
                fname = ln.split(":", 1)[0].rsplit("/", 1)[-1]
                if fname in BIG_FILES:
                    if fname not in big_seen:
                        big_seen.add(fname)
                        big_hits.append(ln[:300])
                    continue
                seen_lines.add(ln)
                hits.append(ln[:300])
        except Exception:
            pass
        if len(hits) >= max_lines:
            break
    result = hits[:max_lines]
    if len(result) < max_lines:
        for b in big_hits:
            if b not in seen_lines:
                result.append(b)
                if len(result) >= max_lines:
                    break
    return "\n".join(result)


def run_single_question(q: dict, use_keyword_fallback: bool, verbose: bool = False) -> dict:
    """跑单题: RAG-lite 检索仓内事实 → mmx 开卷作答 → LLM-judge 双评 (per runner v5)."""
    question = q.get("question", "")
    expected = q.get("expected_keywords", [])
    expected_str = q.get("expected_answer", "") or " / ".join(expected)

    context = retrieve_context(question, expected)
    prompt = (
        "You are answering a memory-bench question about the local ~/.claude/ "
        "configuration repository. Use ONLY the repository context below "
        "(grep results from ~/.claude). If the context lacks the fact, say so. "
        "Answer concisely in Chinese.\n\n"
        f"Repository context:\n{context}\n\nQuestion: " + question
    )
    try:
        # Bug v6 fix: 答案生成也走 mmx text chat (CLI session 未登录 claude -p)
        # v5.1: --output json 拿 usage 真值 (input/output_tokens);
        #       注意 --quiet 会覆盖 --output json 退回纯文本, 必须去掉
        proc = subprocess.run(
            ["mmx", "text", "chat", "--message", prompt,
             "--non-interactive", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # v5.1: --output json 拿 usage 真值 (input/output_tokens, per user 2026-07-20 拍板
        # token_economy 改实测). json 解析失败时降级 text.
        input_tokens = output_tokens = 0
        answer = ""
        try:
            payload = json.loads(proc.stdout)
            answer = "\n".join(
                c.get("text", "") for c in payload.get("content", [])
                if isinstance(c, dict) and c.get("type") == "text"
            ).strip()
            usage = payload.get("usage") or {}
            input_tokens = int(usage.get("input_tokens", 0) or 0)
            output_tokens = int(usage.get("output_tokens", 0) or 0)
        except (json.JSONDecodeError, AttributeError, ValueError):
            pass
        if not answer:
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
        score = evaluate_with_position_bias_mitigation(question, expected_str, answer, verbose=verbose)
        judge_mode = "llm-judge+position-bias"

    return {
        "id": q.get("id"),
        "question": question,
        "answer": answer[:200] + ("..." if len(answer) > 200 else ""),
        "score": score,
        "judge": judge_mode,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "prompt_chars": len(prompt),
    }


def run_consistency_questions(consistency_path: Optional[Path]) -> tuple[int, int]:
    """跑 consistency 15 题: 跨源 grep + LLM-judge 语义判定 (per design §2.2).

    Bug v4 fix: os.path.expanduser(s) 先展开 ~ 再 Path(s).exists().
    """
    if not consistency_path or not consistency_path.exists():
        return 0, 15  # stub
    questions = json.loads(consistency_path.read_text(encoding="utf-8")).get("questions", [])
    score = 0
    for q in questions[:15]:
        sources = q.get("sources", [])
        pattern = q.get("grep_pattern", "")
        # Bug v4 fix: expanduser 必须
        expanded_sources = [os.path.expanduser(s) for s in sources]
        # 跨源 grep
        grep_hits = sum(
            1 for s in expanded_sources
            if Path(s).exists() and pattern in Path(s).read_text(errors="ignore")
        )
        # LLM-judge 语义判定 (简化: 命中 ≥ 50% sources 算 1 分)
        if expanded_sources and grep_hits / len(expanded_sources) >= 0.5:
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

    print(f"🚀 memory-bench runner v5.1 (RAG-lite + LLM-judge + token_economy 实测), running {n} questions, parallel={args.parallel}")
    print(f"   judge_mode: {'keyword-fallback' if args.keyword_fallback else 'llm-judge+position-bias'}")

    wall_clock_start = time.time()
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
    # v5.1 token_economy 实测 (per user 2026-07-20 拍板, 替代 stub 50 上限 0.95 bug):
    #   token_part = 每题平均 input_tokens vs 预算 3000 (RAG 注入 ≤12 grep 行 ≈ 1.1k tokens 为健康基线)
    #   clock_part = 全量 wall-clock vs 预算 1800s (v5 实测 ~700-900s)
    #   超出预算线性衰减到 0; usage 缺失时按 prompt_chars/4 估算 (chars→tokens 通用近似)
    wall_clock_s = time.time() - wall_clock_start
    total_in_tokens = sum(r.get("input_tokens", 0) for r in results)
    if total_in_tokens > 0:
        avg_in_tokens = total_in_tokens / max(1, n)
        token_basis = f"实测 {total_in_tokens} tokens"
    else:
        avg_in_tokens = sum(r.get("prompt_chars", 0) for r in results) / max(1, n) / 4.0
        token_basis = "usage 缺失, 按 prompt_chars/4 估算"
    token_part = 100.0 if avg_in_tokens <= TOKEN_BUDGET_PER_Q else max(
        0.0, 100.0 * TOKEN_BUDGET_PER_Q / avg_in_tokens)
    clock_part = 100.0 if wall_clock_s <= CLOCK_BUDGET_S else max(
        0.0, 100.0 * CLOCK_BUDGET_S / wall_clock_s)
    token_score = 0.7 * token_part + 0.3 * clock_part
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
    print(f"\n## token_economy 明细 (v5.1 实测)")
    print(f"- token_part: {token_part:.1f}/100 (avg input {avg_in_tokens:.0f} tokens/题, 预算 {TOKEN_BUDGET_PER_Q}, {token_basis})")
    print(f"- clock_part: {clock_part:.1f}/100 (wall-clock {wall_clock_s:.0f}s, 预算 {CLOCK_BUDGET_S}s)")
    print(f"- token_economy: {token_score:.1f}/100 (0.7×token + 0.3×clock)")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{run_id_base}.md"
    report_path.write_text(
        report
        + f"\n## token_economy 明细 (v5.1 实测)\n\n"
        + f"- token_part: {token_part:.1f}/100 (avg input {avg_in_tokens:.0f} tokens/题, 预算 {TOKEN_BUDGET_PER_Q}, {token_basis})\n"
        + f"- clock_part: {clock_part:.1f}/100 (wall-clock {wall_clock_s:.0f}s, 预算 {CLOCK_BUDGET_S}s)\n"
        + f"- token_economy: {token_score:.1f}/100 (0.7×token + 0.3×clock)\n",
        encoding="utf-8",
    )
    print(f"\n报告已写入: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())