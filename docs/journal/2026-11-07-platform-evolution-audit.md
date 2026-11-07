# 2026-11-07 — Optional platform architecture and GitHub audit

## Scope and source state

This review started from `main` at `f2ab72b` and the remote GitHub planning
state on 2026-11-07. The reviewed source was the documentation working tree on
`docs/169-platform-evolution`; no code, configuration or runtime dependency was
changed. [#169](https://github.com/gleniosp/fleetforge/issues/169) owns the
documentation delivery. This review supplies planning evidence, not runtime
implementation evidence.

The audit read the README, documentation map, canonical requirements and
traceability, architecture/ADRs, Pixi/Cargo configuration, Rust Agent source,
ROS fixtures, CI workflow and GitHub milestones/issues. The remote inventory
had 27 milestones and 144 issues before this reconciliation. M0/M1 were closed;
M2–M8 and future milestones remained open. Relevant issue comments checked for
#49, #79, #147 and #160 contained no additional discussion.

The repository implements a configured Agent, SQLite identity/assignment
persistence, release integrity/signing tooling and real ROS 2 A/B fixtures.
The local authority, deployment/recovery engine, console and future platform
remain planned. A signed release fixture and accepted architecture do not prove
production security or fleet operation.

## Gap and change matrix

| Capability                                               | Existing coverage                                          | Action                                                    | Milestone                   | Reason                                                              |
| -------------------------------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------- | --------------------------- | ------------------------------------------------------------------- |
| MVP identity, release, coordination and offline recovery | MVP-01–MVP-11, NFR-01–NFR-07, M0–M8                        | Preserve                                                  | Existing                    | Future plans must not alter MVP exit                                |
| Package provider, release registry and delivery          | #51, #64, #96, #100, #158                                  | Extend #51 and architecture                               | FUT-03/FUT-06               | Provider access is separate from approval and authorization         |
| Peer and backend messaging                               | #49, #66, #74, #82                                         | Extend existing issues and architecture; no new milestone | FUT-01/FUT-07/FUT-10/FUT-12 | Different communication domains need different guarantees           |
| Hosted placement, IaC and CI                             | #74, #79, #82, #111                                        | Extend existing issues and proposed reference             | FUT-10–FUT-12               | AWS/OpenTofu choices require evidence and self-hosted comparison    |
| Model artifacts                                          | #160–#164                                                  | Preserve FUT-15; link #160 to training handoff            | FUT-15                      | Existing model release work is already scoped                       |
| Robotics capture and dataset lineage                     | No dedicated issue/milestone                               | Add DATA-01/DATA-02, FUT-17, #170/#171                    | FUT-17                      | Telemetry and release artifacts do not own dataset consent/catalog  |
| External training/evaluation handoff                     | #160 records model evidence but excludes training platform | Add ML-01 and #172                                        | FUT-17                      | Producer output needs separate approval and provenance boundary     |
| Optional commercial services                             | No dedicated contract or issue                             | Add COM-01, FUT-18, #173/#174                             | FUT-18                      | Entitlements/usage cannot control robots                            |
| Cross-cutting future qualities                           | MVP NFRs and existing future issue checks                  | Add FUT-NFR-01/FUT-NFR-02                                 | FUT-12/FUT-17/FUT-18        | Future data/security and hosted resilience need verification owners |

No issue was deleted or closed: the audit did not identify a duplicate that
warranted removal. No new milestone was needed for transport or backend
messaging, because existing FUT-01 and FUT-10–FUT-12 issues can own their
evaluations. FUT-17 and FUT-18 have distinct deliverables and exit evidence.

## Decision status and trade-offs

Accepted MVP decisions remain local authority, direct authenticated WebSocket,
signed immutable releases and local accepted-work recovery. AWS is a preferred
hosted reference candidate; OpenTofu, Prefix.dev, API Gateway/IoT Core,
persistent gateways, MQTT, NATS/Zenoh and PostgreSQL outbox with EventBridge/SQS
remain evaluations, not accepted production selections. The new architecture
pages record alternatives and decision owners. No new ADR was accepted because
the provider, transport and IaC evidence gates have not run. Self-hosted
operation may require more infrastructure maintenance; managed services create
provider-specific limits and costs. Offline operation prevents instantaneous
revocation or remote deletion.

## GitHub reconciliation

Created [FUT-17](https://github.com/gleniosp/fleetforge/milestone/28) and
[FUT-18](https://github.com/gleniosp/fleetforge/milestone/29), with deferred
scope, dependencies, security boundaries and exit tests. Created
[#170](https://github.com/gleniosp/fleetforge/issues/170),
[#171](https://github.com/gleniosp/fleetforge/issues/171),
[#172](https://github.com/gleniosp/fleetforge/issues/172),
[#173](https://github.com/gleniosp/fleetforge/issues/173) and
[#174](https://github.com/gleniosp/fleetforge/issues/174). Updated existing
[#49](https://github.com/gleniosp/fleetforge/issues/49),
[#51](https://github.com/gleniosp/fleetforge/issues/51),
[#66](https://github.com/gleniosp/fleetforge/issues/66),
[#74](https://github.com/gleniosp/fleetforge/issues/74),
[#79](https://github.com/gleniosp/fleetforge/issues/79),
[#82](https://github.com/gleniosp/fleetforge/issues/82),
[#111](https://github.com/gleniosp/fleetforge/issues/111) and
[#160](https://github.com/gleniosp/fleetforge/issues/160). Native blockers were
added to #170–#174 and verified against their descriptions. All five new
delivery issues remain deferred; #169 records documentation work in progress.

## Validation and limits

`pixi run --locked -e host format` and `pixi run --locked -e host check` passed
on the documentation working tree. `git diff --check` passed. A local
file/fragment review of changed Markdown found no broken local target. Remote
milestone numbers, issue assignments, updated body markers and native blocker
lists were read back after writing. The new documents were not reviewed as a
rendered site. Their architecture is planning, not measured implementation.
