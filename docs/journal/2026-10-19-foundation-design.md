# Foundation design evidence — 2026-10-19

**Task:** [M0-01 / issue #1](https://github.com/gleniosp/fleetforge/issues/1)

## Scope and delivery

Prepared the product contract, domain terminology, MVP/future boundaries,
architecture and deployment diagrams, GitHub-linked roadmap, requirement
traceability, documentation ownership, and three initial ADRs.

The maintainer requested a local review before the first commit and push to `main`.
This delivery has no commit/revision or PR yet. The normal PR-only closure policy
continues for subsequent work; the initial exception does not imply manual issue
closure. The detailed working agreement belongs to M0-02.

No toolchain manifest, runtime package, deployment implementation, CI workflow,
license, or placeholder service was introduced by this documentation task.

## Validation method

Review the written contracts against MVP-01 through MVP-11, NFR-01 through NFR-07,
and FUT-01 through FUT-12. Resolve every local Markdown destination/fragment;
compare GitHub issue/milestone links against authenticated API snapshots; inspect
code fences, Mermaid source, final newlines, and trailing whitespace. Check the
GitHub blocker graph for cycles and MVP-to-future edges.

The validation helper is temporary review tooling outside the repository, not a
new project task or supported contributor dependency. Product code, automated
runtime tests, canonical tasks, and CI do not exist yet. Documentation checks are
not evidence that a robot deployment or offline installation works.

## Review-snapshot results

The local check used Python's installed Markdown parser and standard library,
followed by Git working-tree inspection. It checked 11 Markdown files and 197 links,
including 41 local destinations/fragments
and 152 GitHub references against API snapshots. All 21 milestone destinations,
11 MVP requirements, seven non-functional requirements, and 12 future capabilities
were present. Four Mermaid source blocks, final newlines, whitespace, and fences
passed the source checks. The 84-issue blocker graph was acyclic, with no MVP
dependency on future work. No missing link/fragment was reported.

Git inspection confirmed an unborn `main` branch with the documentation files
untracked. Nothing was staged, committed, or pushed during review preparation.
A Git revision will identify the published documents once the initial commit exists.

## Second review: duplication and ownership

After accepting the corrected documents, the maintainer requested a second review
of documentation and GitHub planning density. The initial backlog repeated the
same delivery contract on all 84 issues and workflow guidance on all 21 milestones.

Removed the common contract and three shared completion reminders from each issue,
retaining task-specific criteria, their checked state, validation, and blocker
references. Replaced the repeated policy with a reference to issue #2, which carries
one temporary GitHub baseline until the initial repository policy is published.
Future issue outcomes now describe the individual task instead of repeating the
whole capability. Milestones retain goals, prerequisites, exit criteria, learning
objectives, and optional article topics; GitHub supplies their issue lists.

Issue body text decreased by 75.7%, and milestone descriptions by 68.6%. The live
verification confirmed the same 84 issues, 21 milestones, and 113 native blocker
links, with titles, states, labels, and assignments preserved. All issues remain
open; the graph remains acyclic and the MVP has no future blocker. Two stale
workflow criteria in issue #2 were aligned with the approved initial-publication
exception. No technical acceptance criterion was dropped.

Locally, selection and delivery guidance is owned by the documentation map, the
roadmap links to it, and ADR 0002 explains rationale without repeating the complete
architecture contract. The initial reviewed publication can satisfy issue #1's
delivery prerequisites while the issue awaits closure through a qualifying PR.
The full working agreement/templates remain M0-02 work.

The updated source review checked 11 documents and 200 links, including 45 local
destinations/fragments and 151 GitHub references, with no missing destination.
Requirements and milestone coverage were preserved. No commit or push occurred
during this review.

## Consistency audit

This audits the design and planned verification, not implemented behavior.

| #   | Question                                                        | Resolution and verification owner                                             |
| --- | --------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 1   | Every MVP capability has a milestone and test?                  | Traceability maps all eleven IDs to delivery and verification issues          |
| 2   | Observability starts early?                                     | M2 diagnostics; M3 events; M4 synchronization/API; M6 console                 |
| 3   | Dashboard uses actual state?                                    | MVP-09 and M6-04 require real API/workload assertions                         |
| 4   | Requested, accepted, executing, succeeded and recovered differ? | Ownership/sequence/lifecycle contracts keep them separate                     |
| 5   | Release catalog explicit?                                       | MVP-02 and M1-01 define immutable identity/digest lookup                      |
| 6   | Delivery differs from activation?                               | Setup provisions bytes; protocol sends identity; local lifecycle activates    |
| 7   | Offline installs a fresh environment?                           | MVP-10 A/D and M1-05 require absent target environment and real package bytes |
| 8   | Internet and operator disconnections tested independently?      | MVP-10 A/B/C with positive and negative path probes                           |
| 9   | Single operator authority explicit?                             | Fixed boundary, ADR 0002 and M4-01                                            |
| 10  | Generations durable across restart?                             | MVP-06, M4-02 and M7-06                                                       |
| 11  | Duplicate/stale/conflicting instructions safe?                  | Reconciliation response table and M4-03/M4-06                                 |
| 12  | Database, files and processes reconciled?                       | Crash-consistency invariants and M3-05/M7-05                                  |
| 13  | Recovery differs from requested rollback?                       | Separate definitions; rollback is a new generation                            |
| 14  | Diagnostics bounded and observable?                             | MVP-07; event pruning/gap and API/UI verification                             |
| 15  | Stale reports represented honestly?                             | Freshness contract; M4-05 and M6-02/M6-04                                     |
| 16  | Deterministic fault injection?                                  | M5-03/M7 use actual faults and explicit phase/acceptance barriers             |
| 17  | Docker state independent?                                       | MVP-08; M5-01/M5-04 assert private identities/volumes/caches                  |
| 18  | Bootstrap excludes product infrastructure?                      | MVP-01 and ADR 0001; no runtime files in this task                            |
| 19  | Tasks perform meaningful work?                                  | Task contract and M0-05; no task placeholders created                         |
| 20  | MVP needs no future capability?                                 | Explicit scope boundary and blocker-graph audit                               |
| 21  | Production security limits documented?                          | Trusted-local security boundary and FUT-06 gate                               |
| 22  | Cloud optional to local operation?                              | ADR 0002; central data is projection/administration                           |
| 23  | Investigations bounded and timely?                              | ADR 0003 and milestone-owned experiment table                                 |
| 24  | Docs self-contained and GitHub-consistent?                      | Documentation ownership map, real roadmap links and requirement traceability  |

Additional failure rule: recovered A with desired B remains visibly unsatisfied;
a terminal failed generation does not automatically retrigger indefinitely.

## Evidence limits

During maintainer review, semicolons in the sequence acknowledgment label and
preparation-failure transition label were reported to break Mermaid rendering.
Replaced both with commas and checked all four Mermaid blocks for remaining
semicolons. Re-ran the documentation source/link checks. The maintainer accepted
the corrected documents; no automated rendered-layout check was run.

The documents establish design and intended tests. Full GitHub-rendered Mermaid
appearance and product execution are not established by source/link checks. Exact
versions, SQLite/process guarantees, offline cache behavior, transport behavior,
and network isolation require the bounded experiments listed in the architecture.

Review checks/results belong in repository evidence and the PR. Subsequent
validation and change summaries should not be posted as issue comments. Record
the actual revision when available rather than inventing one in advance; GitHub
issues retain their task scope, dependencies, and acceptance checklist state.
