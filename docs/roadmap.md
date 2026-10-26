# Roadmap

FleetForge moves from an engineering foundation to a real simulated fleet, then
deliberately selected future capabilities. No milestone has an artificial
deadline. The [product requirements](product/requirements.md) own scope; the
[architecture](architecture/overview.md) owns boundaries.

[GitHub milestones](https://github.com/gleniosp/fleetforge/milestones) own
delivery scope, exit criteria, and progress.
[Issues](https://github.com/gleniosp/fleetforge/issues) own acceptance
checklists, blockers, priority, and current review state. This page is
navigation, not a second live task tracker.

## Bootstrap and MVP

| Milestone                                                                                                  | Delivery boundary                                                                                                |
| ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| [M0 — Repository bootstrap](https://github.com/gleniosp/fleetforge/milestone/1)                            | Engineering foundation; no deployment runtime prerequisite                                                       |
| [M1 — Reproducible software releases](https://github.com/gleniosp/fleetforge/milestone/2)                  | Signed ROS 2 Jazzy A/B releases, catalog and fresh cached-install evidence                                       |
| [M2 — Durable robot foundation](https://github.com/gleniosp/fleetforge/milestone/3)                        | Asset/device and assignment identity, SQLite, workload privileges/trust, supervision and diagnostics             |
| [M3 — Local deployment engine](https://github.com/gleniosp/fleetforge/milestone/4)                         | Local preparation, activation, health, recovery and durable events                                               |
| [M4 — Operator and reconciliation](https://github.com/gleniosp/fleetforge/milestone/5)                     | Local authority, authorized mutual TLS WebSocket push, signed instructions, generations and bounded observations |
| [M5 — Simulated fleet infrastructure](https://github.com/gleniosp/fleetforge/milestone/6)                  | Three isolated Compose robots, private credentials/ROS domains and independent network/process faults            |
| [M6 — Operator console](https://github.com/gleniosp/fleetforge/milestone/7)                                | Authenticated SvelteKit selected/all deploy/rollback, bounded events/log tails and honest freshness              |
| [M7 — Offline and resilience validation](https://github.com/gleniosp/fleetforge/milestone/8)               | Independent offline, partition and restart scenarios                                                             |
| [M8 — End-to-end acceptance and contributor readiness](https://github.com/gleniosp/fleetforge/milestone/9) | Full reproducible acceptance and contributor/release readiness                                                   |

M1 releases and M2 agent foundations can progress independently after M0; both
feed M3. Diagnostics begin with M2, durable deployment events with
M3, synchronization/API with M4, isolated fleet evidence with M5, and UI
visibility with M6. Each milestone tests its own failures. M7 integrates
resilience; M8 audits the complete result. Issue-level blocker links define the
exact sequence and supersede assumptions from milestone numbering.

## Future platform

These milestones remain deferred until deliberately activated. Their numbering
is thematic. They are not dependencies of the MVP or robot-local execution.

| Milestone                                                                                              | Decision/dependency boundary                                                                                          |
| ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| [FUT-01 — Advanced P2P networking](https://github.com/gleniosp/fleetforge/milestone/10)                | Extend secure direct WSS with authenticated discovery/membership, justified transports, NAT and optional relays       |
| [FUT-02 — Distributed synchronization](https://github.com/gleniosp/fleetforge/milestone/11)            | Signed/authorized selected-state sharing, per-type conflicts and device-fenced authority transfer                     |
| [FUT-03 — Distributed artifacts and edge caching](https://github.com/gleniosp/fleetforge/milestone/12) | Authorized content-addressed resumable delivery and protected peer/edge caches                                        |
| [FUT-04 — Advanced rollout orchestration](https://github.com/gleniosp/fleetforge/milestone/13)         | Durable admissions/fresh-health gates, partition-safe concurrency, scheduling and pause/resume UI                     |
| [FUT-05 — Robotics integration](https://github.com/gleniosp/fleetforge/milestone/14)                   | Extend MVP ROS 2 with selected Gazebo/advanced robotics and approved physical pilots                                  |
| [FUT-06 — Production security and identity](https://github.com/gleniosp/fleetforge/milestone/15)       | Production enrollment/credential/signing lifecycle, incident response and independent review beyond MVP controls      |
| [FUT-07 — Advanced observability](https://github.com/gleniosp/fleetforge/milestone/16)                 | Optional bounded telemetry export/storage, dashboards and alerts independent of execution                             |
| [FUT-08 — Production device support](https://github.com/gleniosp/fleetforge/milestone/17)              | Validated native/ARM64 matrix, boot supervision, compatible agent/schema upgrades and recovery                        |
| [FUT-09 — Multi-tenancy](https://github.com/gleniosp/fleetforge/milestone/18)                          | Organizations/roles, complete boundary isolation, quotas and ownership transfer with historical privacy               |
| [FUT-10 — Optional central management](https://github.com/gleniosp/fleetforge/milestone/19)            | Tenant-aware PostgreSQL from first migration, explicit local/hosted authority placement and safe projections/restores |
| [FUT-11 — Cloud infrastructure and IaC](https://github.com/gleniosp/fleetforge/milestone/20)           | Service-driven provider/IaC, isolated environments/resources, delivery, secrets/teardown and backup drills            |
| [FUT-12 — Production cloud architecture](https://github.com/gleniosp/fleetforge/milestone/21)          | Decoupled API/jobs/gateways/ingestion/blobs, pooled DB, tenant placement/cells and measured reliability/cost          |

The [future architecture](architecture/future.md) owns guarantees, exclusions
and evidence gates for every deferred capability. Millions of assets/devices are
a measured future target, not an MVP promise. Cloud/SaaS, brokers and site
gateways remain optional; prioritize hardened device operations and peer
reachability/artifact delivery after MVP.

Future issues start with contract/decision gates and carry native blockers for
security, platform, and service prerequisites. Reassess their scope against real
needs before implementation; creating an issue does not authorize speculative
research, paid resources, or hardware operations.

## Find work

Follow the [selection and delivery guidance](README.md#selecting-work).

Browse [ready
issues](https://github.com/gleniosp/fleetforge/issues?q=is%3Aissue+is%3Aopen+label%3Astatus%3Aready),
[review
handoffs](https://github.com/gleniosp/fleetforge/issues?q=is%3Aissue+is%3Aopen+label%3Astatus%3Ain-review),
and [deferred future
work](https://github.com/gleniosp/fleetforge/issues?q=is%3Aissue+is%3Aopen+label%3Ascope%3Afuture).
Historical delivery remains in [closed
issues](https://github.com/gleniosp/fleetforge/issues?q=is%3Aissue+is%3Aclosed)
and [closed
milestones](https://github.com/gleniosp/fleetforge/milestones?state=closed),
with factual evidence in repository journals, experiments, and Git history.

The [delivery boundary](README.md#delivery-boundary) owns local review, commit
authorization, PR publication and maintainer approval/merge rules.
