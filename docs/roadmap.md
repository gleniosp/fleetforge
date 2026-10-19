# Roadmap

FleetForge moves from an engineering foundation to a real simulated fleet, then
deliberately selected future capabilities. No milestone has an artificial deadline.
The [product requirements](product/requirements.md) own scope; the
[architecture](architecture/overview.md) owns boundaries.

[GitHub milestones](https://github.com/gleniosp/fleetforge/milestones) own delivery
scope, exit criteria, and progress. [Issues](https://github.com/gleniosp/fleetforge/issues)
own acceptance checklists, blockers, priority, and current review state. This page
is navigation, not a second live task tracker.

## Bootstrap and MVP

| Milestone | Delivery boundary |
| --- | --- |
| [M0 — Repository bootstrap](https://github.com/gleniosp/fleetforge/milestone/1) | Engineering foundation; no deployment runtime prerequisite |
| [M1 — Reproducible software releases](https://github.com/gleniosp/fleetforge/milestone/2) | Real A/B releases, catalog and early cached-install evidence |
| [M2 — Durable robot foundation](https://github.com/gleniosp/fleetforge/milestone/3) | Agent identity, SQLite, supervision and early diagnostics |
| [M3 — Local deployment engine](https://github.com/gleniosp/fleetforge/milestone/4) | Local preparation, activation, health, recovery and durable events |
| [M4 — Operator and reconciliation](https://github.com/gleniosp/fleetforge/milestone/5) | Operator authority, direct protocol, generations and observations |
| [M5 — Simulated fleet infrastructure](https://github.com/gleniosp/fleetforge/milestone/6) | Three independent Compose robots and deterministic fixtures |
| [M6 — Operator console](https://github.com/gleniosp/fleetforge/milestone/7) | SvelteKit controls, diagnostics and honest freshness |
| [M7 — Offline and resilience validation](https://github.com/gleniosp/fleetforge/milestone/8) | Independent offline, partition and restart scenarios |
| [M8 — End-to-end acceptance and contributor readiness](https://github.com/gleniosp/fleetforge/milestone/9) | Full reproducible acceptance and contributor/release readiness |

M1 releases and M2 agent foundations are independent after M0; both feed M3.
Diagnostics begin with M2, durable deployment events with M3, synchronization/API
with M4, isolated fleet evidence with M5, and UI visibility with M6. Each milestone
tests its own failures. M7 integrates resilience; M8 audits the complete result.
Issue-level blocker links define the exact sequence and supersede assumptions from
milestone numbering.

## Future platform

These milestones remain deferred until deliberately activated. Their numbering is
thematic. They are not dependencies of the MVP or robot-local execution.

| Milestone | Decision/dependency boundary |
| --- | --- |
| [FUT-01 — Advanced P2P networking](https://github.com/gleniosp/fleetforge/milestone/10) | Security-gated discovery/transport, NAT and relays |
| [FUT-02 — Distributed synchronization](https://github.com/gleniosp/fleetforge/milestone/11) | Explicit authority/conflict model before replication and convergence |
| [FUT-03 — Distributed artifacts and edge caching](https://github.com/gleniosp/fleetforge/milestone/12) | Trusted artifact delivery before distributed/edge caches |
| [FUT-04 — Advanced rollout orchestration](https://github.com/gleniosp/fleetforge/milestone/13) | Durable deployment/health observations before progressive rollout |
| [FUT-05 — Robotics integration](https://github.com/gleniosp/fleetforge/milestone/14) | Reproducible robotics simulation before secured physical pilots |
| [FUT-06 — Production security and identity](https://github.com/gleniosp/fleetforge/milestone/15) | Threat model, enrollment/authentication/authorization, release trust |
| [FUT-07 — Advanced observability](https://github.com/gleniosp/fleetforge/milestone/16) | Stable identity/events before optional fleet telemetry and alerts |
| [FUT-08 — Production device support](https://github.com/gleniosp/fleetforge/milestone/17) | Validated platform matrix before native operations and agent upgrades |
| [FUT-09 — Multi-tenancy](https://github.com/gleniosp/fleetforge/milestone/18) | Production security and service boundaries before tenant isolation |
| [FUT-10 — Optional central management](https://github.com/gleniosp/fleetforge/milestone/19) | Projection/ownership contract before optional central management |
| [FUT-11 — Cloud infrastructure and IaC](https://github.com/gleniosp/fleetforge/milestone/20) | Concrete service needs before provider/IaC and paid deployment |
| [FUT-12 — Production cloud architecture](https://github.com/gleniosp/fleetforge/milestone/21) | Measured service workloads before production cloud runtime choice |

Future issues start with contract/decision gates and carry native blockers for
security, platform, and service prerequisites. Reassess their scope against real
needs before implementation; creating an issue does not authorize speculative
research, paid resources, or hardware operations.

## Find work

Follow the [selection and delivery guidance](README.md#selecting-work).

Browse [ready issues](https://github.com/gleniosp/fleetforge/issues?q=is%3Aissue+is%3Aopen+label%3Astatus%3Aready),
[review handoffs](https://github.com/gleniosp/fleetforge/issues?q=is%3Aissue+is%3Aopen+label%3Astatus%3Ain-review),
and [deferred future work](https://github.com/gleniosp/fleetforge/issues?q=is%3Aissue+is%3Aopen+label%3Ascope%3Afuture).
Historical delivery remains in [closed issues](https://github.com/gleniosp/fleetforge/issues?q=is%3Aissue+is%3Aclosed)
and [closed milestones](https://github.com/gleniosp/fleetforge/milestones?state=closed),
with factual evidence in repository journals, experiments, and Git history.

The [delivery boundary](README.md#delivery-boundary) owns review/merge rules and the
one-time initial publication exception.
