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
| [Working agreement](working-agreement.md) | Task selection, delivery permissions, review/commit/publication flow, issue sizing, and milestone exit |
| [Contributing](../CONTRIBUTING.md) | Public issue validation, fork/PR submissions, and optional global GitHub CLI usage |
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

Evidence journals: [foundation review](journal/2026-10-19-foundation-design.md),
[architecture consolidation](journal/2026-10-20-architecture-consolidation.md),
and [task delivery guidance](journal/2026-10-20-task-delivery.md).

Requirements describe expected behavior. The traceability table describes
intended verification, not passing tests. GitHub owns current work state; avoid
copying live task checklists or completion percentages into repository
documents.

## Delivery boundary

The [working agreement](working-agreement.md) owns
[implementation/readiness](working-agreement.md#implementation-and-readiness),
[local review, commits, and publication](working-agreement.md#review-commits-and-publication),
and [GitHub state/milestone exit](working-agreement.md#github-state-and-milestone-exit).
Start with [CONTRIBUTING.md](../CONTRIBUTING.md) for contributor navigation or
[AGENTS.md](../AGENTS.md) for agent guidance and repository skills.

## Selecting work

Follow [Selecting work](working-agreement.md#selecting-work) and
[Branches and issue sizing](working-agreement.md#branches-and-issue-sizing).
GitHub owns live priorities, blockers, and review state; the roadmap is navigation.

## Bounded upstream collaboration

The agreement's [permissions and upstream policy](working-agreement.md#permissions-and-upstream-collaboration)
owns reproducer/handoff requirements, specifically authorized contributions,
and temporary workaround ownership. [ADR 0003](adr/0003-bounded-decisions-and-evidence.md)
owns bounded investigation and evidence quality.
