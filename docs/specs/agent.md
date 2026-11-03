# Agent identity and configuration

**Status:** Implemented for the Linux x86_64 agent foundation in #15.
SQLite persistence is owned by #16; runtime permissions and trust provisioning by
#87. [Identity](../architecture/identity.md) owns lifetimes and assignment rules.

## Provisioning and retention

`fleetforge-agent --new-id PATH` allocates a canonical uppercase ULID using a
48-bit Unix millisecond timestamp and 80 bits of OS randomness. Randomness and
clock failures are errors. The destination uses exclusive creation: an existing
file, including a symlink, is a provisioning conflict and is never overwritten.
A failed write may leave a partial file; preserve and inspect it before recovery.
The file is synced before success. This is local allocation, not a registry:
operators must check uniqueness in their inventory before assigning an ID.
Concurrent registration and database uniqueness errors belong to #16/#26.

Allocate asset/device IDs and an assignment record for the managed endpoint;
reuse the existing tenant and authority IDs for their owner and deployment writer.
All five identity types use the canonical ULID representation in this configuration
version. The Rust
asset and device types are distinct. The parser rejects aliases, lowercase,
wrong lengths, non-ASCII input and values above 128 bits. The agent rejects
identical asset/device values and mismatched assignment bindings explicitly.
IDs are public identifiers and grant no permission.

Keep the configuration and provisioned ID files across restart, software update
and credential rotation. Hardware replacement retains the asset ID but receives
a new device ID and explicit assignment. A clone must receive new device identity
and credentials before use. Never regenerate lost identity automatically: recover
it from the operator inventory, or explicitly retire it and provision a replacement.
Retired IDs must remain reserved in that inventory. No enrollment, transfer,
reset or retirement service is implemented here.

## Configuration format

Run `fleetforge-agent --config PATH` with a UTF-8 TOML regular file of at most
16 KiB. Unknown fields, missing fields and invalid IDs reject the whole file;
parser diagnostics do not echo its contents. All fields below are required:

```toml
asset_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
device_id = "01ARZ3NDEKTSV4RRFFQ69G5FAW"
state_dir = "/var/lib/fleetforge"
runtime_dir = "/run/fleetforge"
authority_endpoint = "wss://localhost:8443/agent"

[assignment]
asset_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
device_id = "01ARZ3NDEKTSV4RRFFQ69G5FAW"
tenant_id = "01ARZ3NDEKTSV4RRFFQ69G5FAX"
authority_id = "01ARZ3NDEKTSV4RRFFQ69G5FAY"
assignment_id = "01ARZ3NDEKTSV4RRFFQ69G5FAZ"
```

The endpoint must be an absolute `wss` URI with a host, an optional nonzero
16-bit port, and no credentials or fragment. It is validated only; networking is
not implemented.

The top-level `asset_id` and `device_id` identify this agent's configured endpoint.
The corresponding fields inside `[assignment]` identify the endpoint bound to
that tenant/authority relationship. Both pairs must match; a mismatch rejects
startup. Matching values establish local configuration consistency only. The
parser cannot establish that an authority authorized the assignment, and changing
both pairs together is not detected as a mismatch. Trusted provisioning and the
[security contract](../architecture/security.md) own authorization checks.

Paths must be existing,
absolute, canonical, non-root directories with neither containing the other.
The agent neither creates nor modifies those directories in this slice.
Canonical-path validation is a startup consistency check; it does not enforce
ownership, permissions or prevent concurrent filesystem replacement. Provision
trusted local configuration and directories; #87 owns the OS security boundary.

Startup configuration I/O and instance allocation run on one blocking worker
with a five-second deadline. Runtime shutdown waits at most one additional
second for a stalled worker; the CLI exits and the OS reclaims remaining threads.
This does not cancel a kernel filesystem operation. No state is written by startup.

## Liveness and diagnostics

The configured process installs SIGINT/SIGTERM handlers and emits JSON events
on stderr: `agent_started`, `agent_liveness` every five seconds, and
`agent_stopped`. Each event carries timestamp, component, asset/device,
tenant/authority/assignment and a fresh ephemeral `agent_instance`. A liveness
event is produced by the actual Tokio loop; it is not a workload health check.
Workload process is `absent`, health is `unknown`. There are no managed children,
management listeners, authority connection or durable events yet.

A dedicated tracing writer has a bounded 128-line lossy queue so a stalled sink
cannot block the event loop. Logs may be dropped; they are not durable evidence
of every transition. Shutdown has no workload to drain. The writer guard makes a
bounded flush attempt (up to 100 ms to enqueue shutdown and one second for its
acknowledgment in locked tracing-appender 0.2.5); a blocked sink may lose final
logs. No indefinitely blocking writer is joined at exit.

Usage errors exit 2; configuration/runtime/provisioning failures exit 1;
normal diagnostic/help/version and graceful signal shutdown exit 0. The existing
no-argument bootstrap diagnostic remains available.
