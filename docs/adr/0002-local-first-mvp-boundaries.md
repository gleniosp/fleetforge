# ADR 0002 — Local-first MVP ownership and recovery

- **Status:** Accepted architectural constraints; implementation pending.
- **Date:** 2026-10-19
- **Updated:** 2026-10-20
- **Requirements:** [MVP-02–10](../product/requirements.md#functional-requirements)
- **Delivery:** [M1](https://github.com/gleniosp/fleetforge/milestone/2),
  [M2](https://github.com/gleniosp/fleetforge/milestone/3),
  [M3](https://github.com/gleniosp/fleetforge/milestone/4),
  [M4](https://github.com/gleniosp/fleetforge/milestone/5)

## Context

Robots must continue local operation during unreliable connectivity. Desired
intent, observed status, persistent metadata, files, and real OS processes have
different owners and failure boundaries. Centralized imperative execution would
make operator availability part of each deployment's critical path.

## Decision

Use one local logical Rust/Tokio deployment authority and three autonomous
Rust/Tokio device agents. Persist requested intent at the operator and
execution/recovery state at each robot in separate SQLite databases. Durable
acceptance separates authority from execution; the operator can disappear
without invalidating accepted local work. Direct configured communication keeps
the initial coordination model small. There is one writer per assignment; peer
membership grants no authority. Internet loss permits new local deployments when
the authority and trusted inputs remain reachable; authority loss before
delivery leaves intent pending. Credential expiry constrains new network
authorizations without cancelling accepted local work. Authority transfer
requires device-side fencing; unreachable transfer stays pending.

Pre-provision immutable releases and package bytes so deployment correctness can
be verified independently of artifact distribution. FleetForge owns application
activation, supervision, health, and recovery; Pixi owns environment
installation.

Treat restart recovery and operational visibility as correctness requirements.
Database commits cannot cover OS processes or filesystem changes, and
disconnected observations are necessarily uncertain. These constraints require
explicit reconciliation and bounded durable diagnostics from the beginning.

The [coordination contract](../architecture/coordination.md) owns instruction,
offline, restore-quarantine and freshness semantics; the
[overview](../architecture/overview.md) owns deployment/supervision invariants.
[ADR 0006](0006-signed-trust-and-privilege-boundaries.md) owns the MVP security
boundary. [ADR 0004](0004-asset-device-and-tenancy.md) owns identity/tenancy;
[ADR 0005](0005-authenticated-push-transport.md) selects transport. [ADR
0001](0001-pixi-cargo-and-task-ownership.md) owns Pixi/FleetForge
responsibility. The [requirements](../product/requirements.md) own scope and
acceptance; this ADR records why those boundaries were selected rather than
duplicating their contracts.

## Alternatives and consequences

Continuous operator-driven execution would simplify initial coordination but
weaken local autonomy. Multi-master state or artifact distribution would expand
conflict and security concerns beyond this MVP. Simulated status-only
deployments would produce no evidence about real installation, health,
supervision, or recovery.

The chosen model requires explicit acknowledgment, retries, restart
reconciliation, and honest stale-state reporting. It accepts temporary workload
interruption during activation/agent restart. It does not promise cross-resource
transactionality, zero downtime, exactly-once delivery, unlimited history, or
production security readiness.

## Evidence and revisit conditions

[SQLite's atomic commit documentation](https://www.sqlite.org/atomiccommit.html)
describes database transaction behavior; it does not extend that boundary to
robot processes. [Tokio process
documentation](https://docs.rs/tokio/latest/tokio/process/index.html) warns that
dropping a child handle normally leaves the process running. These are reasons
to test supervision and crash recovery explicitly, not evidence that the
FleetForge strategy is already safe.

Revisit a fixed scope decision only for a demonstrated incompatibility or
compelling technical reason, with updated contracts/planning/tests. Supervision
and SQLite settings need focused experiments. Transport is selected; its limits
and failure behavior need implementation evidence. Future local/hosted authority
placement may change reachability for new intent, while device-local accepted
execution/recovery remains independent. Ambiguous stale authority restores
quarantine instead of replaying uncertain intent; projection rebuilds cannot
issue commands.
