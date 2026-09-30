# Host / local-system evolution mode

Use this mode for the user's local Agent control planes and development host: `~/.agents`,
`~/.claude`, `~/.codex`, skills, shell/runtime, hooks, local CI/recovery, instruction projections,
memory/context routing and related machine-level drift.

The former `host-self-evolve` skill has been absorbed here. Its old SKILL is historical. The
remaining `host-self-evolve/scripts/`, references and reports are legacy implementation/evidence
assets; they do not own current workflow semantics.

## Start with identity and current truth

Before modifying host state:

1. resolve the actual machine/device and current working directory;
2. identify canonical repositories/branches and dirty/uncommitted work;
3. refresh `.agents`, `.claude` and `.codex` current owners;
4. inspect active processes/writers when shared config files may be concurrently modified;
5. separate generated projections from writable sources;
6. identify which checks are current executable truth versus dated historical scripts.

Do not hardcode old shell versions, model versions, local paths, quotas or remembered tool lists.

## Host review lanes

Inspect only the lanes relevant to current facts, but a full host evolution run should consider:

### 1. Shared instruction and projection topology

- one writable shared owner for shared semantics;
- generated Claude/Codex projections are not competing truth stores;
- stale duplicated rules/adapters are candidates for retirement;
- current root/bootstrap context stays small and routes to task-specific owners.

### 2. Shell, runtime and environment

- actual login/process shell versus assumed shell;
- current Python/Node/package-manager ownership;
- broken PATH/init/permission assumptions;
- duplicated environment configuration and dead loaders;
- executable smoke checks for anything repaired.

Do not "unify" shells or runtimes solely for aesthetic symmetry.

### 3. Skills, hooks and automation

- active skill inventory, duplicate responsibilities and stale aliases;
- hooks that are actually mounted versus historical reference implementations;
- dead commands/scripts and orphaned adapters;
- whether native/runtime capability now replaces custom machinery;
- whether safe routine work is unnecessarily blocked on manual confirmation.

### 4. Memory and context

- current memory owner and retrieval path;
- stale or duplicated hot instructions;
- candidate memory being mistaken for policy;
- large always-loaded context that should become warm/cold;
- session/compaction recovery through compact structured state.

Never bulk-delete memories/history merely to reduce volume.

### 5. CI, guards and recovery

- executable host/harness invariants;
- provider-neutral validation versus hosted execution;
- false-green scripts, skipped/dead checks and stale path assumptions;
- recovery paths for shared config changes;
- separation of provider/infrastructure failure from code/policy failure.

## Reusable legacy host tools

The following tools remain available as implementation assets while they are useful:

- `../../host-self-evolve/scripts/dead_code_detector.py`
- `../../host-self-evolve/scripts/commands_to_skills_migrator.py`
- `../../host-self-evolve/scripts/lint_runner.py`
- `../../host-self-evolve/scripts/memory_audit_runner.py`
- `../../host-self-evolve/scripts/skill_authoring_checker.py`
- `../../host-self-evolve/scripts/skill_overlap_enhancer.py`
- `../../host-self-evolve/scripts/waste_token_detector.py`
- `../../host-self-evolve/scripts/auto_fix_proposer.py`
- `../../host-self-evolve/scripts/harness_invariants.py`

Use them when their current schema/assumptions still fit. A legacy script is not authority merely
because CI still exercises it.

The six historical consistency dimensions under
`../../host-self-evolve/references/consistency-6d/` remain useful as a checklist:
terminology, cross-references, rule conflicts, index validity, frontmatter and priority/scope.
Apply them proportionally instead of forcing every run through a fixed ritual.

## What is retired from the old host workflow

Do **not** preserve these as mandatory current behavior:

- run-start banners or fixed long output templates;
- arbitrary wall-clock expectations;
- fixed numbers of search tools/sources;
- mandatory multi-agent Planner/Executor/Verifier theater for simple work;
- historical model/shell/version constants;
- retired memory benchmarks or quotas;
- automatic ADR creation for routine maintenance;
- "ask the user" gates for ordinary safe repairs already authorized.

Keep historical records as evidence only.

## Host verification closeout

For changed host surfaces, verify the layers actually touched. Useful closeout fields are:

- **path/owner** — canonical writable source resolved;
- **change** — exact files/configuration affected;
- **local executable evidence** — syntax/tests/smoke/invariant output;
- **repository state** — commit/PR/current-base status when tracked;
- **hosted/live evidence** — only when a live provider/runtime is part of acceptance;
- **rollback/recovery** — known for consequential host config changes.

A full host run should end with no unexplained high-confidence drift in the scoped control planes.
