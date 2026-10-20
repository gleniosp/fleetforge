---
name: task-delivery
description: Select the next FleetForge issue or carry agreed work through implementation, validation, local review, and commit-message handoff.
---

# FleetForge task delivery

Read the [working agreement](../../../docs/working-agreement.md) for the
applicable stage and use the [documentation map](../../../docs/README.md) to
find owning contracts. The agreement owns permissions and completion rules.

- For next-task requests, follow [Selecting work](../../../docs/working-agreement.md#selecting-work):
  inspect live milestone/issue scope, native blockers and actual merged delivery,
  then recommend the earliest active unblocked issue by priority and stable task
  ID, with a branch name. Report blocked/access-limited findings explicitly.
- For implementation, confirm the maintainer's agreed issue and actual branch
  using [Branches and issue sizing](../../../docs/working-agreement.md#branches-and-issue-sizing).
  Read the issue's criteria and owning contracts, then deliver the complete slice
  under [Implementation and readiness](../../../docs/working-agreement.md#implementation-and-readiness).
  Preserve unrelated work. Keep ordinary checks with delivery evidence; use the
  [experiment-evidence skill](../experiment-evidence/SKILL.md) for a concrete
  technical uncertainty.
- Hand off the changes, validation/evidence, and remaining limits for local
  review. For commit-message requests, return Conventional Commit text under
  [Review, commits, and publication](../../../docs/working-agreement.md#review-commits-and-publication).
  Do not infer Git publication authority from implementation or message requests.
- For PR content, publication, or PR feedback, read the
  [pull-request skill](../pull-request/SKILL.md) and apply the agreement to the
  actual request. Track scope/checklists through
  [GitHub ownership](../../../docs/working-agreement.md#github-state-and-milestone-exit);
  keep validation and delivery summaries out of issue comments.

Use available file/Git/GitHub tools. The agreement's CLI examples are optional
read-only access paths, not prerequisites or project validation tasks.
