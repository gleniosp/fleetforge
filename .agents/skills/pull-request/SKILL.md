---
name: pull-request
description: Prepare FleetForge PR content, publish reviewed commits when requested, or handle PR feedback under the maintainer's delivery agreement.
---

# FleetForge pull requests

Read [Review, commits, and publication](../../../docs/working-agreement.md#review-commits-and-publication)
and [GitHub state and milestone exit](../../../docs/working-agreement.md#github-state-and-milestone-exit).
Use the [PR template](../../../.github/pull_request_template.md) for content.

Identify the requested action: content preparation, explicit publication,
committed update, or local feedback work. Apply the agreement's authorization
table; a prepared title/body is a text artifact, and task implementation alone
does not authorize publication.

Inspect the current default branch, complete branch diff and commit series,
staged/unstaged/untracked work, agreed issue criteria, and repository evidence.
Check for an existing branch PR and its base, review state, and scope. Resolve
uncommitted or unreviewed work under the agreement before publication, accounting
for all branch changes rather than only the latest commit.

Describe the final problem/result, evidence/revision/limits, and readiness. For
coherent multiple-issue work, follow
[Branches and issue sizing](../../../docs/working-agreement.md#branches-and-issue-sizing)
and give each completely delivered issue its own closure reference. Reconcile
changed scope in the title/body. Use draft status for incomplete work; a ready
PR must meet every claimed issue's criteria and required checks.

On explicit raise-PR authorization, push the reviewed commits and create the
default-branch PR, or reuse its existing PR. Use available GitHub tooling; with
`gh`, pass multiline bodies through `--body-file`. Report the PR URL and current
review/readiness state.

For feedback, inspect the comments and full current change, address the requested
work locally, and revalidate affected behavior. Update owning evidence and
prepare revised PR content as needed. Follow the agreement's local review and
commit/publication steps; maintainer approval and merge remain the final gate.
