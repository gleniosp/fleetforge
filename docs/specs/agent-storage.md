# Agent identity storage

Implemented by #16 for the Linux x86_64 agent. See [identity](../architecture/identity.md)
for identity lifetimes and [ADR 0008](../adr/0008-agent-sqlite-storage.md) for the choice.

## Creation and reopening

Configured startup exclusively creates `state_dir/identity-store/` on first use,
syncs its parent, then creates `identity.sqlite3`. This retained directory is the
initialization marker. Existing stores must contain a regular database with schema
version 1 and a matching identity. Missing, empty, corrupt, unsupported or incomplete
stores fail startup with exit 1 before liveness. Initialization errors leave all
artifacts for inspection. Never remove them merely to retry.

A completely lost state volume cannot be distinguished from a new volume by local
software. Operators must retain the whole state directory and configuration, and
restore them together from trusted inventory/backups after loss. No automatic ID
generation, database replacement or re-enrollment occurs. Filesystem ownership
and protection against hostile concurrent replacement belong to #87.

## Version 1

The executable migration is
[0001_identity.sql](../../apps/agent/migrations/0001_identity.sql), embedded into
[storage.rs](../../apps/agent/src/storage.rs) at compile time. SQLite `user_version` is the schema
version. An immediate transaction creates the strict tables, inserts the configured
binding and advances the version together. Failure rolls back all three.

`assignments` stores assignment, asset, device, tenant and authority IDs. Assignment
ID is its primary key; asset and device must differ. The singleton `identity` row
references the current assignment through a foreign key. On reopen all five
values must exactly match validated configuration. Missing rows and dangling
references are errors. Assignment rows retain their original context; no update,
transfer or historical relabeling API exists. Deployment tables arrive with #19–#23.

## Transactions and ownership

All SQLite access currently occurs once in the existing startup blocking worker,
with one connection and no request queue or runtime database API. Tokio workers
perform no synchronous database I/O. Startup has a five-second deadline and runtime
shutdown waits one additional second; a timed-out blocking operation is not
cancelled and may still write before process exit. Inspect failed initialization
before explicit recovery. Later runtime writes require a bounded dedicated owner.

Each connection enables foreign keys, FULL synchronous durability and WAL,
checks database integrity with `quick_check`, and checks foreign-key consistency.
Busy handling waits at most 500 ms per operation with no application retry. This
is a small tolerance for overlapping startup attempts. For example, during a
restart, the supervisor could start a replacement while the old process is still
checking the same database. The timeout is not a single-instance guard: it does
not prevent two processes from sharing the state directory. An agent closes its
startup connection before serving, so a normally running old process does not
keep the database locked.
Local writable storage must support SQLite locking, shared memory and sync;
network filesystems are unsupported. Keep WAL sidecars with the database during
recovery; use SQLite backup or stop the agent before copying its store.

Durability depends on filesystem/device sync behavior. SQLite transactions do
not include processes or arbitrary files. Disk-full, permission, lock and I/O
errors reject startup; no healthy-running event is emitted before commit and
directory sync. The agent closes its startup connection before serving.
There is no ongoing database growth in this slice.

Tests and limits are recorded in the [delivery evidence](../journal/2026-11-04-agent-storage.md).

The current bundled SQLite is the validated baseline.
[Agent delivery](../architecture/agent-delivery.md) and #145 own validation and
adoption of Pixi-provided SQLite; the intended deployment model does not change
this schema or make packaging part of #16.
