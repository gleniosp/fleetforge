# Working agreement

This document owns FleetForge's maintainer-led, agent-assisted task delivery.
[CONTRIBUTING.md](../CONTRIBUTING.md) owns the public issue and fork/PR contribution
process. Agent instructions, skills, and templates route to these owners rather
than copying their rules.

## Ownership and precedence

Within repository policy, the latest explicit maintainer direction takes
precedence. Apply scoped instructions within their directory while inheriting
general guidance; they must not silently change shared delivery permissions or
product contracts. Resolve conflicting scope before dependent work and continue
independent authorized work where possible. Update affected owners and planning
when direction changes.

The [documentation map](README.md) owns the source map: requirements own product
scope; architecture and ADRs own contracts and decisions; GitHub issues own task
scope, dependencies, priority, and checklists; milestones own exit criteria and
progress. Journals/experiments and PRs own factual evidence. Skills assist with
these contracts and do not establish competing policy.

## Selecting work

When the maintainer asks for the next task:

1. Fetch current GitHub issues, milestone priorities/exit criteria, native blocker
   links, and related PR/review state. Start with the earliest active bootstrap
   or MVP milestone unless directed otherwise. Future scope requires explicit
   activation, even when its milestone is open.
2. Check actual dependency delivery. A checked box, local implementation, closed
   issue without delivery evidence, or unmerged PR does not establish a merged
   prerequisite. Inspect linked merged PRs/default-branch evidence. Work awaiting
   review needs its review handoff, not an automatic implementation restart.
3. Recommend an active open issue with delivered prerequisites, ordered by
   priority and then stable task ID, and propose its branch name. Labels aid
   discovery; stale `ready` or `backlog` labels do not override dependencies.
4. Read the owning requirements, contracts, ADRs, and existing evidence. If all
   candidates are blocked, report the smallest missing prerequisite. If live
   access is unavailable, disclose that readiness cannot be confirmed.

For example, these read-only global GitHub CLI commands inspect M0 and a selected
issue; they are not project tasks:

```sh
gh issue list --repo gleniosp/fleetforge --state open \
  --milestone "M0 — Repository bootstrap" --limit 100
gh issue view 2 --repo gleniosp/fleetforge
gh api repos/gleniosp/fleetforge/issues/2/dependencies/blocked_by
gh pr list --repo gleniosp/fleetforge --state open
```

Substitute the selected issue and inspect each blocker's associated delivery.
Do not infer a global dependency order from milestone numbers.

## Branches and issue sizing

Use `<type>/<issue-number>-<short-description>`, for example
`docs/2-maintainer-task-delivery` or `feat/15-device-identity`. Recommend a name,
then use the branch the maintainer creates, or create/switch it when explicitly
instructed. Inspect the actual branch and working tree before editing; preserve
unrelated work and resolve a wrong branch before implementation.

Normally use one issue and one PR for one independently reviewable behavior or
focused decision, including essential tests/configuration/documentation.
Split independently testable behavior before implementation. There is no fixed
line/file limit, artificial issue-count cap, placeholder-crate requirement, or
separate follow-up for essential safety tests. Integration issues verify
completed slices rather than absorb missing implementation.

A coherent combined delivery uses the first issue number in its branch and a
broader description. Include complete work for each issue, make internal
dependency order reviewable, and include a separate `Closes #N` for each delivered
issue. An unmerged prerequisite can be included only as part of that complete
combined PR; unrelated dependent work still waits for merged delivery.

## Implementation and readiness

Repository `check`, `format-check` and CI are read-only. The installed Prek
pre-commit hook may run repository-wide host `fix`, including eligible
untracked files. Changes to tracked/staged files stop the commit for review and
restaging; do not automatically stage fixes. Preserve unstaged tracked edits
through Prek's snapshot and conflict recovery behaviour. Untracked files remain
visible and may be formatted. Device formatting remains explicitly scoped.

Implement the agreed scope on its agreed branch. Resolve a concrete missing
contract through a focused decision or bounded experiment under
[ADR 0003](adr/0003-bounded-decisions-and-evidence.md). Accepted design is not
runtime evidence; do not add speculative future infrastructure or no-op tasks.

A review-ready delivery contains its complete code, essential tests,
migrations/configuration, documentation, and necessary decisions/evidence.
Run validation relevant to the change, including meaningful failure cases, and
report only checks actually performed. Record reproducible commands, repository
inputs, versions, results, source revision, and limits in the owning evidence and
PR. Do not cite temporary paths or files absent from the repository as validation
evidence; label manual review explicitly. Identify uncommitted work as the
working tree based on a known revision rather than inventing a future commit ID.
Report unavailable checks or failed assumptions explicitly. A ready PR must
contain everything required to move to dependent work after merge; a draft may
expose clearly described incomplete work.

Check acceptance criteria only when supported by the delivered artifacts and
evidence. Finish implementation with a concise local review handoff describing
the change, validation, and remaining limits. Leave the working tree available
for maintainer review.

## Review, commits, and publication

This sequence governs actions an agent performs on behalf of the repository
maintainer. External contributors manage their fork commits and submissions
through the [public contribution process](../CONTRIBUTING.md#submit-a-pull-request-from-your-fork).
Repository maintainers validate issues and PRs and own approval and merging into
`main`; an exploratory PR may help validate an issue before its scope is accepted.

For maintainer-agent work, the maintainer leads implementation through local
review, commits, publication, and PR review. Authorization persists across
requests, but applies only to the operations actually requested:

| Maintainer request                             | Authorized next action                                                                                 |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Find the next task                             | Read live scope and recommend an issue and branch                                                      |
| Work on the issue on the created/agreed branch | Implement, validate, and leave changes for local review                                                |
| Give a commit message                          | Return Conventional Commit text only                                                                   |
| Create a commit                                | Perform the explicitly requested commit of reviewed work                                               |
| Prepare PR content                             | Return title/body text for review                                                                      |
| Raise the PR                                   | Inspect Git state/full branch diff, push reviewed commits, and create the PR or reuse the existing one |
| Address review feedback                        | Make and validate requested changes locally, then follow the same review/commit flow                   |
| Publish committed updates                      | Push the reviewed commits and update the existing PR as requested                                      |

Implementation alone does not authorize staging, commits, pushes, or PR
creation. A commit-message request never executes a commit. The maintainer
controls commits and may request several focused commits on one branch. Use
Conventional Commit subjects: `<type>(<optional-scope>): <description>`, with a
short imperative description and a body when rationale is needed. Typical
types are `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, and `chore`;
use `!` or a `BREAKING CHANGE:` footer only for an actual breaking change.
Keep each commit coherent and independently understandable. Include an issue
reference such as `Refs #6` in the body when useful; the complete delivery's PR
owns issue closure.

Before publication, discover the repository's current default branch, compare
the complete branch diff and commit series against that base, inspect staged,
unstaged, and untracked work, and check for an existing PR for the branch.
Account for every change. Uncommitted work needs local review/commit disposition
before publication; report it instead of silently committing or omitting it.
If reviewed commits contain unrelated or unreviewed changes, resolve their
disposition before pushing. Use an existing PR rather than create a duplicate;
inspect its base, scope, and current review first.

PR titles and bodies describe the final change for a reviewer without chat
context. Include the concrete problem/result, delivered scope and closure
references, validation evidence/revision/limits, and incomplete work for drafts.
Review the full diff even when there are multiple commits. Readiness covers every
claimed issue and required check; do not label incomplete work ready.

Wait for maintainer PR review. Inspect feedback against the full current change,
address it locally, explain technical disagreements with evidence, and resolve
scope changes with the maintainer. Revalidate affected behavior and update
owning documents/evidence and PR content to match the final result. Follow the
same local review, commit, and requested publication sequence for corrections.
Only the maintainer approves and merges. Agents must not self-approve, merge,
or enable auto-merge. Select another task when asked after merge.

## GitHub state and milestone exit

Issues own scope, native blockers, priority, and acceptance checklists. Keep
blocker text and native links aligned when authorized scope changes. Validation
commands/results, delivery summaries, and change feedback belong in repository
evidence and PRs, not issue comments. Record only evidenced checklist completion.

Before raising or updating a PR, reconcile every corresponding issue's
description, acceptance and validation checklists, and dependencies with the
agreed delivered scope. Before marking the PR ready for final maintainer review,
all applicable issue checklist items must be completed and checked with evidence.
Do not check unsupported items or remove unfinished requirements merely to make
the checklist pass; keep incomplete work explicit in a draft PR. Include a
separate `Closes #<issue-number>` in the default-branch PR body for every fully
delivered issue. The number identifies the issue, not the PR. GitHub closes the
issue when the maintainer merges the PR; approval alone does not close it.
Keep the issue open until that merge and never close it manually.

Milestone completion requires every scoped delivery and its exit evidence, not
just no remaining unchecked boxes. Inspect merged deliveries, requirement
traceability, and integration/failure evidence against the milestone's actual
exit criteria. Report remaining gaps to the maintainer; close a milestone only
after its scoped deliveries and exit evidence are complete and closure is
authorized. Future activation is a deliberate scope decision, independent of
whether GitHub calls the milestone open.

## Permissions and upstream collaboration

Use the narrowest tool, filesystem, credential, and network permissions needed
for the agreed operation. Existing task authorization does not grant unrelated
external writes or broader access. If an environment approval blocks a necessary
action, request that specific action and explain the restriction; do not bypass
it or request broad persistent grants. Reuse authorization already given.
Protect unrelated local changes and credentials; keep secrets and private keys
out of source, evidence, and public output. Paid resources, destructive drills,
and hardware operations need task-specific authorization.

For a concrete Pixi, rattler, or RoboStack gap, preserve a minimal reproducer and
assess current upstream capabilities. An upstream issue or contribution belongs
to the affected delivery when specifically authorized; otherwise record an
actionable handoff with reproduction, relevant versions, observed/expected
behavior, and impact. Temporary workarounds need an owner and removal condition.
Bound research by the active question and a useful stopping condition. Personal
learning preferences do not expand product scope.
