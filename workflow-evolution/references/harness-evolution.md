# Harness evolution mode

Use this mode when changing Agent harnesses, skills, prompts, hooks, tool routing, context/memory,
orchestration, sandboxes, approvals, verification architecture or cross-harness adapters.

The former `harness-upgrade` skill has been absorbed here. Its historical SKILL remains under
`_archive/harness-upgrade/`; this reference is the current workflow.

## Mandatory current research refresh

For a substantive harness change:

1. refresh current runtime/config/skill ownership and the exact versions/surfaces actually in use;
2. **search the web before editing** for current official vendor/platform guidance;
3. use **recent primary research** for general claims about agent/harness improvement when possible;
4. seek **disconfirming evidence**, not only evidence supporting the proposed change;
5. record applicability: finding → affected surface → why it applies here → design consequence;
6. if current evidence does not justify a change, keep the current design.

At minimum, use a current first-party source for every affected platform whose behavior may have
changed. A general claim such as "this orchestration pattern improves agents" needs independent
primary evidence or a local experiment; product marketing alone is insufficient.

On a future run, perform **the research refresh again**. The source list below is provenance, not
permanent policy.

## 2026-10 refresh: load-bearing current evidence

- OpenAI, *Rethinking skills and prompts for GPT-6 Astra*:
  https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
  - keep skill descriptions short and trigger-specific;
  - for multi-workflow skills, use a minimal root router plus supporting files/scripts;
  - remove scaffolding that newer models no longer need;
  - when a workflow is known safe, explicitly authorize the Agent to execute/fix/rerun rather than
    forcing repeated approval;
  - define completion so the Agent does not stop after the first implementation.
- OpenAI, *Skills*:
  https://developers.openai.com/api/docs/guides/tools-skills
  - skills are modular reusable instructions;
  - keep main instructions in SKILL.md and place background/scripts/assets in supporting paths.
- OpenAI, *Harness engineering*:
  https://openai.com/index/harness-engineering/
  - make the environment directly inspectable and enforce architecture through machine invariants;
  - treat failures as feedback about missing tools, guardrails or legibility.
- Anthropic, *Scaling Managed Agents: Decoupling the brain from the hands*:
  https://www.anthropic.com/engineering/managed-agents
  - harness assumptions go stale as models improve;
  - prefer stable interfaces and replaceable underlying implementation.

### Design consequence for this repository

These sources support one canonical evolution workflow with progressive disclosure and fewer
competing active skill descriptions. They argue **against** copying the old harness-upgrade and
host-self-evolve bodies into one giant hot prompt.

## Design defaults to test, not eternal laws

### Keep the core loop simple

Prefer harness-native execution, sandboxing, approvals, shell/file tools, skills, compaction,
tracing and platform-native primitives over bespoke wrappers that duplicate them.

### Progressive disclosure

Classify context as:
- **HOT** — must be visible for nearly every run;
- **WARM** — discoverable/loaded only for the selected mode;
- **COLD** — archive/forensic evidence.

Move low-frequency procedure out of hot context before rewriting it shorter in place.

### Structured state over transcript hoarding

For long work, preserve compact goals, decisions, blockers, tested evidence and next actions in an
existing durable owner. Resume from that state rather than replaying an entire transcript.

### Minimize irrelevant tool/context exposure

Expose the tools and instructions required for the selected role/mode. Do not mirror every tool,
hook or skill across harnesses merely for symmetry.

### Bounded autonomy

Use sandbox/least privilege and explicit technical boundaries as the primary safety mechanism.
Inside a known-safe boundary, prefer end-to-end execution over ad-hoc prompt gates.

### Specialize only when specialization pays

Use separate agents/roles when they reduce context interference, enable independent verification or
parallelize separable work. Do not force Planner/Executor/Verifier role theater on every change.

## Context-engineering gate

When changing always-loaded instructions, memory or tool routing:

1. identify HOT/WARM/COLD material;
2. remove stale/duplicated HOT instructions;
3. prefer stable owner links and task-specific discovery;
4. verify machine-enforced startup markers before deleting prose;
5. preserve structured state across compaction/session boundaries;
6. where practical, compare representative before/after behavior rather than judging by line count.

Do not assume a fixed context-window size or one model's limitation is permanent.

## Verification portfolio

Choose evidence appropriate to the change:

- static/config ownership checks;
- executable unit/integration/CLI tests;
- environment fingerprint for runtime-dependent claims;
- independent or pass-2 review;
- user-intent/acceptance evidence;
- adversarial review for permissions/routing/publication/memory changes;
- fresh-Agent acceptance when conversation-context transfer matters.

Never convert an unavailable hosted gate into PASS.

## Safe sequence

1. refresh owners/runtime/callers;
2. research current platform assumptions;
3. state **KEEP / CHANGE / RETIRE / TEST FIRST**;
4. make the smallest coherent reversible change at the canonical owner;
5. add or update machine invariants for load-bearing design choices;
6. verify locally and through the owning hosted gate;
7. refresh moving main/open work before merge;
8. integrate shared semantics before thin adapters when ordering matters;
9. perform post-merge verification;
10. keep only compact durable evidence for substantive architecture changes.
