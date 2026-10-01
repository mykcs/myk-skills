# Safe autonomous repair

Workflow evolution is intended to reduce repeated owner babysitting. When the user asks to evolve,
modernize, align or repair the system, safe engineering work in that scope should normally be
performed, not merely recommended.

## Directly act when all are true

Proceed without another approval when the action is:

- within the user's requested/standing authorized engineering scope;
- non-destructive or readily reversible;
- semantically understood and supported by current evidence;
- not crossing a credential/security/visibility/spending/production decision boundary;
- not overwriting an unresolved active writer;
- protected by an applicable validation or read-back path.

Examples include:

- repository documentation/owner/router fixes;
- safe code/config changes with tests and rollback in Git;
- updating stale audit expectations after an architecture change;
- adding or repairing tests/guards;
- creating branches/PRs and merging through existing required gates;
- removing obsolete active skill routing while preserving history;
- running local tests, audits and read-only live-state checks;
- fixing failures introduced by the requested change and rerunning affected checks.

Before push/merge, inspect automatic effects: tags/releases, site publication, runtime deployment,
Cron activation, public preview and notification delivery. A harmless-looking documentation change
can publish. Complete the reviewable patch and required checks first; request only the missing
concrete side-effect approval. Reuse specific existing approval without asking again, then carry
that action through actual publication and read-back. Invoking this Skill does not grant spending,
new credentials, public exposure or scientific/GPU execution authority.

## Continue instead of stopping early

After the first implementation:

1. inspect the actual result;
2. run affected validation;
3. diagnose failures;
4. repair failures caused by the work;
5. refresh moving state;
6. complete merge/integration when the existing workflow authorizes it;
7. verify post-merge/current state.

Do not return merely because an initial patch exists.

If one target is blocked, continue independent safe work and report the narrow blocker.

## Real stop/approval boundaries

Pause for user input only when needed for:

- destructive deletion/reclamation without existing exact authorization;
- credential/secret value entry or sensitive identity decision;
- new spending, paid capacity or financial commitment;
- public/private visibility or license change;
- production cutover or other irreversible external side effect not already authorized;
- unresolved scientific identity/meaning that would change a claim;
- unresolved ownership;
- an active-writer conflict where safe integration cannot be determined;
- a subjective preference choice where evidence cannot determine the answer.

Existing branch protection, provider approval and safety mechanisms remain in force. "Safe autonomy"
never means bypassing gates, weakening checks, fabricating evidence or crossing administrator
boundaries.

## Prefer reversible engineering structure

For consequential changes:

- use isolated branches/worktrees or atomic repository writes;
- keep the prior route recoverable until the new route qualifies;
- bind acceptance to the exact candidate;
- preserve history/evidence instead of rewriting it;
- verify current state after merge/migration.

Safety should make the workflow more autonomous inside clear boundaries, not more hesitant
everywhere.
