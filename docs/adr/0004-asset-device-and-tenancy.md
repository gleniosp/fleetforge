# ADR 0004 — Asset/device identity and tenancy context

- **Status:** Accepted design; implementation pending.
- **Date:** 2026-10-20
- **Delivery:** [M2-01](https://github.com/gleniosp/fleetforge/issues/15) and
  [M2-02](https://github.com/gleniosp/fleetforge/issues/16).

## Context

A maintainable robot can outlive a managed computer. Treating a hostname,
process, certificate or hardware serial as the robot ID would couple
replacement, ownership and credential rotation. Deferring all tenant context
would make early durable history ambiguous when assignments later change.

## Decision

Separate strongly typed canonical uppercase ULID asset/device IDs from tenant,
logical authority, assignment and ephemeral agent-instance identities. Carry
ownership/assignment context from the first schema with one configured tenant.
The [identity contract](../architecture/identity.md) owns validation,
allocation, replacement/clone/recovery rules and historical privacy.

## Alternatives and consequences

A single robot/device ID is smaller initially but cannot cleanly preserve an
asset through computer replacement. Names/MACs/serials bind identity to mutable
or issuer-scoped metadata. Canonical typed ULIDs support explicit persistent
identity without embedding placement or ownership. They still need secure
generation, uniqueness-conflict handling and strict parsing; they provide no
authorization.

Tenant context is schema preparation, not a multi-tenant management
implementation. Keeping asset-to-many-devices possible does not authorize
multi-device orchestration. Historical assignment context adds migration/access
requirements but prevents later ownership changes from relabeling private
history.

## Sources, evidence and revisit conditions

The [ULID specification](https://github.com/ulid/spec) defines the
format/overflow boundary. FleetForge chooses stricter uppercase canonical input.
No runtime parser, uniqueness or migration evidence exists yet. Require
malformed/overflow/collision, restart, replacement/clone and assignment-mismatch
tests with implementation. Revisit representation only for demonstrated
compatibility needs while preserving identity lifetime and ownership separation.
