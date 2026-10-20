# Documentation map

Use one authoritative owner for each fact and link to it from other documents.
The latest explicit maintainer direction takes precedence; update affected
contracts, decisions, planning, and verification together when direction
changes. Current contracts describe the present design and workflow. Keep useful
status/date metadata and decision rationale, alternatives and consequences; record
edit history and reasons for revisions in journals, issues, PRs and Git history.

| Source | Owns |
| --- | --- |
| [Product requirements](product/requirements.md) | Vision, terminology, scope, requirements, exclusions, and product acceptance |
| [Architecture](architecture/overview.md) | Component/lifecycle boundaries and navigation to identity, coordination, security, and future architecture contracts |
| [ADRs](adr/README.md) | Significant decisions, alternatives, rationale, consequences, and revisit conditions |
| [Roadmap](roadmap.md) | Navigation to GitHub milestones |
| [Traceability](traceability.md) | Requirement links to delivery owners, planned components, and verification methods |
| [GitHub issues](https://github.com/gleniosp/fleetforge/issues) | Live task scope, dependencies, priority, checklists, and review/merge progress |
| [GitHub milestones](https://github.com/gleniosp/fleetforge/milestones) | Delivery grouping, milestone exit criteria, and progress |
| [Journals](#reading-design-and-evidence) | Factual implementation/review evidence and limitations |

Specifications will be introduced alongside the behavior they define.
Experiments will record focused uncertainties when their milestones need
evidence. Guides will document real commands and workflows once available. Blog
drafts may explain verified milestone results without becoming requirements or
task trackers.

## Reading design and evidence

- **Accepted design** means the maintainer has accepted a product or architectural
  constraint. It does not mean that software implements it.
- **Proposed default** means an implementation choice still needs its bounded
  validation experiment and, when significant, its own ADR.
- **Implemented** means the behavior exists in the relevant code/configuration.
- **Verified** requires linked evidence of an appropriate check or actual behavior.

Evidence journals: [foundation review](journal/2026-10-19-foundation-design.md)
and [architecture consolidation](journal/2026-10-20-architecture-consolidation.md).

Requirements describe expected behavior. The traceability table describes
intended verification, not passing tests. GitHub owns current work state; avoid
copying live task checklists or completion percentages into repository
documents.

## Delivery boundary

An implementation is ready for review when its complete code, tests, migrations,
configuration, documentation, and decision/evidence updates are present
together. Run relevant validation and record commands, results, revision, and
limitations in the repository evidence and PR. Check only acceptance criteria
supported by that evidence. Issues own scope, dependencies, and checklist state;
do not add delivery, validation, or change-summary comments. Keep those details
in code, documentation, and the PR rather than duplicating them on the issue.
Draft PRs may expose incomplete work; ready PRs must include everything needed
to move to dependent work after merge.

The maintainer leads each task through this sequence:

1. When asked for the next task, fetch current GitHub scope, dependencies and
   milestone priorities, then recommend an issue and a branch name. Use the
   branch the maintainer creates, or create/switch it when explicitly instructed.
2. Implement the agreed issue on that branch, run relevant checks, and leave the
   changes available for local review. Implementation authorization does not
   authorize staging, committing, pushing or creating a PR.
3. After local review, provide a Conventional Commit message when asked. A
   commit-message request authorizes text only. The maintainer controls commits;
   create a commit only on explicit instruction. A branch may contain multiple
   focused commits, each following the review/message flow as needed.
4. When explicitly asked to raise a PR, inspect the complete branch diff and Git
   state, push the reviewed commits, and create the PR against the default
   branch. That request authorizes the push and PR creation together. Check for
   an existing PR first; uncommitted changes need review/commit disposition
   before publication and must not be silently committed or omitted.
5. Wait for the maintainer's PR review. Address requested feedback locally using
   the same review/commit flow; publish committed updates when requested. The
   maintainer exclusively owns approval and merge. Agents must not self-approve,
   merge, or enable auto-merge.
6. After merge, repeat the process when the maintainer asks for the next task.

An implemented issue remains open until its default-branch PR containing
`Closes #N` merges. Do not manually close it. Dependencies normally require
merged delivery, not checked boxes or an unmerged PR.

Use `<type>/<issue-number>-<short-description>` for branches, for example
`docs/85-consolidate-architecture` or `feat/15-device-identity`. Start with one
issue and one PR. If a coherent delivery needs multiple issues, use the first
issue number in the branch and broaden its description; include a separate
`Closes #N` reference for every delivered issue. A combined PR must include all
required work for those issues and make their dependency order reviewable.

Size an issue around one independently reviewable behavior or focused design
decision, with its essential tests/configuration/documentation in the same PR.
Split independently testable behavior before implementation. There is no fixed
line/file limit, artificial three-issue cap, placeholder-crate requirement, or
separate follow-up for essential safety tests. Integration issues verify
existing slices rather than absorb missing implementation.

The full working agreement, agent/contributor instructions, templates, and
repository task-delivery, pull-request and experiment-evidence skills are owned
by [M0-02](https://github.com/gleniosp/fleetforge/issues/2).

## Selecting work

1. Inspect the earliest active bootstrap/MVP milestone in the [roadmap](roadmap.md),
   unless the maintainer directs otherwise. Future work requires explicit activation.
2. Choose an open, unblocked issue by priority and then stable task ID. Check actual
   dependency delivery, not just labels; review-ready work is awaiting review, not
   another implementation pass.
3. Read its owning requirements, contracts, ADRs, and evidence. Resolve missing
   contracts through a focused decision or experiment before coding.
4. Deliver the complete slice under the review contract above. If every candidate
   is blocked, report the smallest missing prerequisite instead of expanding scope.

For example, inspect M0 using the global GitHub CLI (not a project task):

```sh
gh issue list --repo gleniosp/fleetforge --state open \
  --milestone "M0 — Repository bootstrap" --limit 100
gh issue view 85 --repo gleniosp/fleetforge
gh api repos/gleniosp/fleetforge/issues/85/dependencies/blocked_by
```

Substitute the selected issue number in the last two commands. Labels are
discovery aids; native blockers and review/merge evidence determine readiness.

## Bounded upstream collaboration

For a concrete Pixi, rattler, or RoboStack gap, preserve a minimal reproducer
and assess existing upstream capabilities. An upstream issue or contribution
belongs to the affected delivery only when specifically authorized; otherwise
record an actionable handoff. Give temporary workarounds an owner and a removal
condition. Do not require speculative forks or open-ended research. Explain
decisions and evidence in ADRs and PRs; personal learning preferences do not
expand product scope.
