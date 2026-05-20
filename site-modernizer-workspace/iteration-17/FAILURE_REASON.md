# Iteration-17 Failure Analysis

## Root Cause
1. **Parallel Bash `cp` commands interfered**: Three parallel `cd && cp` Bash calls caused mock repos to be cross-contaminated. All iteration-17 mock repos ended up as `performance` mock repo content.
2. **Agent `cwd` inheritance**: Background agents inherit the session working directory, not the path mentioned in the prompt. All 6 agents ran in the same directory.

## Impact
- anti-pattern & i18n evals ran on wrong mock repo → results meaningless
- performance agents ran in the same directory → modifications overwritten, no commits

## Fix for Iteration-18
- Sequential mock repo copying (no parallel `cp`)
- Agent prompts MUST include explicit `cd <target-dir>` as first step
- Verify agent cwd from transcript before claiming results valid
