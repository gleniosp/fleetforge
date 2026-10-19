# Documentation map

Use one authoritative owner for each fact and link to it from other documents.
The latest explicit maintainer direction takes precedence; update affected
contracts, decisions, planning, and verification together when direction changes.

| Source | Owns |
| --- | --- |
| [Product requirements](product/requirements.md) | Vision, terminology, scope, requirements, exclusions, and product acceptance |
| [Architecture](architecture/overview.md) | Component boundaries, ownership, reconciliation, failure and observability model |
| [ADRs](adr/README.md) | Significant decisions, alternatives, rationale, consequences, and revisit conditions |
| [Roadmap](roadmap.md) | Navigation to GitHub milestones |
| [Traceability](traceability.md) | Requirement links to delivery owners, planned components, and verification methods |
| [GitHub issues](https://github.com/gleniosp/fleetforge/issues) | Live task scope, dependencies, priority, checklists, and review/merge progress |
| [GitHub milestones](https://github.com/gleniosp/fleetforge/milestones) | Delivery grouping, milestone exit criteria, and progress |
| [Journal](journal/2026-10-19-foundation-design.md) | Factual implementation/review evidence and limitations |

Specifications will be introduced alongside the behavior they define. Experiments
will record focused uncertainties when their milestones need evidence. Guides
will document real commands and workflows once available. Blog drafts may explain
verified milestone results without becoming requirements or task trackers.

## Reading design and evidence

- **Accepted design** means the maintainer has accepted a product or architectural
  constraint. It does not mean that software implements it.
- **Proposed default** means an implementation choice still needs its bounded
  validation experiment and, when significant, its own ADR.
- **Implemented** means the behavior exists in the relevant code/configuration.
- **Verified** requires linked evidence of an appropriate check or actual behavior.

Requirements describe expected behavior. The initial traceability table describes
intended verification, not passing tests. GitHub owns current work state; avoid
copying live task checklists or completion percentages into repository documents.

## Delivery boundary

An implementation is ready for review when its complete code, tests, migrations,
configuration, documentation, and decision/evidence updates are present together.
Run relevant validation and record commands, results, revision, and limitations in
the repository evidence and PR. Check only acceptance criteria supported by that
evidence. Issues own scope, dependencies, and checklist state; do not add delivery,
validation, or change-summary comments. Keep those details in code, documentation,
and the PR rather than duplicating them on the issue.
Draft PRs may expose incomplete work; ready PRs must include everything needed to
move to dependent work after merge.

Agents may create focused branches, Conventional Commits, pushes, and PRs for
authorized tasks. The maintainer exclusively owns approval and merging; agents
must not self-approve, merge, or enable auto-merge. An implemented issue remains
open until its default-branch PR containing `Closes #N` merges. Do not manually
close it. Dependencies normally require merged delivery, not checked boxes or an
unmerged PR; related issues may be delivered together in one complete, coherent PR.

For the initial foundation documents only, the maintainer requested local review
before the first commit and push to `main`. That reviewed initial publication
satisfies issue #1's delivery prerequisite for subsequent tasks even while the
issue remains open. It does not authorize manual closure or bypassing review for
later work. A subsequent qualifying PR can include `Closes #1` once the maintainer
confirms that its final acceptance is satisfied.

The full working agreement, agent/contributor instructions, and templates are
owned by
[M0-02](https://github.com/gleniosp/fleetforge/issues/2).

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
gh issue view 1 --repo gleniosp/fleetforge
gh api repos/gleniosp/fleetforge/issues/1/dependencies/blocked_by
```

Substitute the selected issue number in the last two commands. Labels are discovery
aids; native blockers and review/merge evidence determine readiness.
