# Identity and ownership

**Status:** Accepted contract; schema and runtime implementation pending. [ADR
0004](../adr/0004-asset-device-and-tenancy.md) records the decision and
rationale.

## Identity model

| Identity | Meaning and lifetime |
| --- | --- |
| `asset_id` | Maintainable robot; may survive replacement of a managed computer |
| `device_id` | Managed computer/endpoint; stable across restart, software update and credential rotation |
| `tenant_id` | Owning tenant, distinct from network topology and deployment authority |
| `authority_id` | Logical deployment writer, distinct from its host/process/connection |
| `assignment_id` | Binding of asset, device, owning tenant and logical authority |
| Agent instance | Ephemeral process incarnation, separate from persistent device identity |

`asset_id` and `device_id` are distinct strongly typed canonical uppercase
ULIDs. Validate exactly 26 Crockford characters from
`0123456789ABCDEFGHJKMNPQRSTVWXYZ`, with first character `0`–`7`. Reject
malformed, lowercase, aliased and overflowing input at canonical boundaries. Use
secure randomness, allocate once and persist; handle uniqueness conflicts
explicitly rather than overwriting an existing record. The [ULID
specification](https://github.com/ulid/spec) defines the underlying format;
FleetForge deliberately requires the uppercase canonical representation.

IDs are identifiers, neither secrets nor authorization. They do not encode
tenant, location, shard, region or network address. Generation order comes from
durable authority counters, not ULID timestamps. Names, serials, MAC addresses
and issuer-scoped external identifiers remain metadata with explicit issuer
context.

## Assignment and history

An asset has one owning tenant; attached devices must have compatible ownership.
An assignment identifies the authorized relationship and single deployment
writer. The first MVP schema carries tenant, asset, device, assignment and
authority context, starting with one configured tenant and three assets, each
with one device/agent. Keep asset-to-many-devices possible without implementing
multi-device orchestration.

Persist original tenant/assignment context on historical records. A later
ownership change must not relabel old records into another tenant or disclose
the previous tenant's history. Production transfer must revoke old access and
fence execution as specified by the future tenancy/authority work. IDs alone
never grant access; [security](security.md) owns credential and registry checks.

## Lifecycle and recovery

- Restart, software update and credential rotation preserve device identity.
- Hardware replacement gets a new device ID; its asset may remain the same.
- Clones require new identity and credentials before becoming managed endpoints.
- Lost/reset identity requires explicit recovery/enrollment. Retired IDs are never reused.
- Configuration and persisted identity/assignment mismatch fail explicitly.
- Corrupt or unreadable SQLite never triggers silent state replacement or enrollment.

This contract does not define a production enrollment or transfer service. The
first implementation specifies recovery/operator actions and migratable schemas
alongside its tests rather than generating replacement identity on startup
failure.

## Delivery and evidence

[M2-01 (#15)](https://github.com/gleniosp/fleetforge/issues/15) implements typed
IDs, strict parsing and configuration; [M2-02
(#16)](https://github.com/gleniosp/fleetforge/issues/16) persists
identity/assignment and tests migrations, restart, mismatch and corruption.
[M2-05 (#87)](https://github.com/gleniosp/fleetforge/issues/87) provisions trust
and permissions; [M4-02 (#26)](https://github.com/gleniosp/fleetforge/issues/26)
carries these bindings into authority inventory. Require
malformed/overflow/collision, replacement/clone and historical-context evidence
at the owning slices. Full ownership transfer and role isolation belong to
[FUT-09](future.md#fut-09--tenancy).
