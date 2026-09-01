# Recurring engineering failure gates

Read this reference for permission/writeability failures, exact-resume recovery,
or test commands that fail because the server host lacks project dependencies.
It is an execution guard, not a scientific authorization or a replacement for
the host-specific policy.

## Root-first control plane

- Host-side Git, Docker, staging, ownership handoff, and test orchestration use
  the parent-approved root operator path (`wangrui_root` on `lyg2171`; the
  currently documented root/operator path for `whs512`, once its authority is
  resolved). `wangrui_user` is not the default, and this skill must not invent a
  whs512 root command from historical credentials.
- `1001:1001` is an isolated payload identity only. It never determines the SSH
  account, host authority, or permission to mutate shared Docker state.
- Do not “fix” a failed handoff by `chmod 777`, by giving the payload a Docker
  socket, or by mutating another project’s container.

## UID write gate before first generation

Use this whenever a non-root payload writes append-only artifacts such as
`text-memory/`, recovery logs, manifests, or selection receipts:

1. Root creates a fresh run/recovery namespace with the contract’s owner/mode.
2. After model/adapter loading and before the first generation or material call,
   execute a target-runtime probe as `1001:1001` that creates needed directories,
   writes a small file, and atomically renames it in every output root.
3. If any mkdir/write/rename fails, stop before model calls, carrier creation,
   or formal credit. Grant only the exact ownership handoff required by policy;
   never widen the whole tree.

## Append-only recovery and identity

- Validate manifest, contract, source SHA, runtime/image, model/adapter/config,
  and UUID identities before resuming. A mismatch fails closed.
- Reuse a matching write-once selection receipt; do not reselect inputs or
  overwrite a receipt. A same-semantics exact-resume may continue only the
  unused eligible work.
- Each retry/recovery gets a new monotonic immutable container name and fresh
  output namespace. Existing files are write-once: identical content may be
  reused, conflicting content is an error, and failed evidence is never deleted
  or rewritten as PASS.
- If receipts prove `0` model calls, `0` carriers, and `0` formal credit, classify
  the attempt as engineering-only and preserve its exact evidence; do not infer
  this classification from an absent log alone.

## Test-environment routing

- Select the test runner from the project/runtime contract. A server host Python
  without `pytest` is an environment fact, not a reason to install or upgrade
  host packages.
- Preserve the first failed command and exit status. On the host, use only
  zero-install checks such as `py_compile`, authority/source-SHA validation,
  topology/config validators, and immutable image identity checks.
- Run the full pytest suite inside the frozen project Docker image or declared
  project venv where pytest is part of the contract. Do not change activation,
  CUDA, GPU allocation, or scientific inputs just to make tests pass.

## Evidence to retain

Record the failed command, first error, operator/runtime UID, path and mode,
manifest/hash comparison, selection-receipt decision, container name, image
identity, whether GPU/activation changed, and the replacement validation results.
An engineering failure can be exactly resumed only when these identities and the
frozen scientific semantics still match.
