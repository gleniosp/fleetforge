# Agent identity storage — 2026-11-04

Delivery: [#16](https://github.com/gleniosp/fleetforge/issues/16), on
`feat/16-persist-agent-identity`, based on `bcb883c`. The implementation was
validated at `98d4b49`; later changes to the guide and this journal are
documentation-only. The [storage specification](../specs/agent-storage.md) and
[ADR 0008](../adr/0008-agent-sqlite-storage.md) own the implemented contract.

## Delivered behavior

Configured startup creates or validates
`state/identity-store/identity.sqlite3`. The embedded version-1 migration is
stored at `apps/agent/migrations/0001_identity.sql`. The database binds the
asset, device, tenant, authority and assignment IDs. Reopening with different
values fails before the agent reports startup. Missing, corrupt, unreadable,
incomplete or unsupported state is preserved and rejected; the agent never
silently recreates it.

SQLite uses foreign keys, WAL, `synchronous=FULL` and a 500 ms busy timeout.
Exclusive store-directory creation prevents concurrent first provisioning, and
the directory remains as a marker if the database is later lost. Keep the whole
state directory for recovery. The current implementation uses rusqlite 0.41.1
with bundled SQLite 3.54.1. Its Linux x86_64 C build uses the compiler and sysroot
already supplied by the locked Pixi Rust environment. Dependency licenses and
notices are recorded in [THIRD_PARTY.md](../../THIRD_PARTY.md).

This is the source-built Linux x86_64 baseline, not the installed Pixi agent
runtime. ADR 0009 and the [delivery architecture](../architecture/agent-delivery.md)
record the intended Pixi/pixi-pack path. Issue [#145](https://github.com/gleniosp/fleetforge/issues/145)
owns its packaging and Pixi-provided SQLite validation before #87 uses that
layout. No installer, updater, cross-platform device support or migration runner
is implemented in #16; assess a maintained migration runner before adding a
second schema version.

## Validation

Validated on Linux x86_64 with Pixi 0.83.0 and Rust/Cargo 1.98.1. The final
implementation checks passed:

- `pixi run --locked -e device agent-test`: 26 tests passed (6 unit, 10 CLI,
  10 configured-process tests).
- `pixi run --locked -e device agent-check`: formatting and Clippy passed.
- `pixi run --locked -e device agent-build`: locked executable build passed.
- `pixi run --locked -e host format` and
  `pixi run --locked -e host check`: passed.
- `git diff --check` and manual source/documentation review: passed.

The tests use real temporary SQLite files. They cover fresh migration and
reopen, graceful and SIGKILL restart, each configured binding mismatch,
corrupt/missing/incomplete/future-version state, unreadable-file preservation,
foreign-key and durability settings, lock timeout, invalid store paths and
transaction rollback on SQLite's `SQLITE_FULL` error. The unreadable-file case
ran as UID 1000 because root bypasses normal Unix permission checks.

GitHub's PR workflow has not run because no PR is open. On PR creation it checks
the host on Linux x86_64, Linux ARM64 and macOS Apple Silicon, the device build
and tests on Linux x86_64, and the offline release regression.

## Limits

`SQLITE_FULL` was simulated with SQLite's page limit; no physical full-disk,
failed-fsync or power-cut test was run. Whole-volume loss cannot be detected
without external inventory. There is no native ARM/macOS device validation or
workload/agent permission-isolation claim; #87 owns runtime trust and permissions.
The offline workload suite was not rerun for this storage-only change.
