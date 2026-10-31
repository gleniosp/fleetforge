# Documentation map

Use one authoritative owner for each topic and link to it elsewhere. Documents
outside journals and experiment reports describe the current implementation,
workflow, or accepted design/plans. Keep revision narratives and superseded
implementation details in journals or relevant experiment evidence. Preserve
those records as dated evidence, with corrections rather than rewritten results.
ADRs retain current decisions and their rationale, alternatives, consequences
and revisit conditions; creation/update dates and status are useful metadata.

Code and configuration own executable details; guides explain workflows and
non-obvious constraints.

| Area                                   | Owns                                                                              |
| -------------------------------------- | --------------------------------------------------------------------------------- |
| [Product](product/README.md)           | Requirements, acceptance and shared terminology                                   |
| [Guides](guides/README.md)             | Explanations, contributor workflows and operational instructions                  |
| [Architecture](architecture/README.md) | Component boundaries and lifecycle, identity, coordination and security contracts |
| [Specifications](specs/README.md)      | Shared formats and detailed interface rules                                       |
| [ADRs](adr/README.md)                  | Significant decisions, rationale and revisit conditions                           |
| [Experiments](experiments/README.md)   | Bounded technical investigations and reproducible evidence                        |
| [Journals](journal/README.md)          | Dated delivery evidence and limitations                                           |
| [Examples](../examples/README.md)      | Release fixtures, conformance inputs and ROS demonstrations                       |
| [Schemas](../schemas/)                 | Authoritative machine-readable contracts                                          |

The [project README](../README.md) owns current capabilities and first run.
The [roadmap](roadmap.md) links delivery milestones; [traceability](traceability.md)
maps requirements to implementation and verification owners. The
[working agreement](working-agreement.md) owns maintainer task delivery, and
[CONTRIBUTING](../CONTRIBUTING.md) owns public contribution workflows.
[GitHub issues](https://github.com/gleniosp/fleetforge/issues) own live scope,
blockers, priority and checklists; [milestones](https://github.com/gleniosp/fleetforge/milestones)
own exit criteria and progress. Root policy files own licensing, provenance,
security reporting and community conduct.

Specifications accompany the behavior they define.

## Reading design and evidence

- **Accepted design** means the maintainer has accepted a product or architectural
  constraint. It does not mean that software implements it.
- **Proposed default** means an implementation choice still needs its bounded
  validation experiment and, when significant, its own ADR.
- **Implemented** means the behavior exists in the relevant code/configuration.
- **Verified** requires linked evidence of an appropriate check or actual behavior.

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
