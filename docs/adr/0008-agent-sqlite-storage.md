# ADR 0008 — Agent SQLite identity storage

- **Status:** Implemented for #16.
- **Date:** 2026-11-04
- **Delivery:** [M2-02](https://github.com/gleniosp/fleetforge/issues/16)

## Decision

Use rusqlite with bundled SQLite for the agent's first durable identity schema.
This is the validated #16 baseline. [ADR 0009](0009-pixi-agent-delivery.md) selects
Pixi-delivered agent runtimes as intended architecture; #145 must validate and
adopt Pixi-managed SQLite before this implementation changes.
Keep its single startup operation on the existing bounded blocking worker.
The [storage specification](../specs/agent-storage.md) owns schema, error,
recovery and transaction behavior. Use WAL, FULL synchronous commits, foreign
keys and a 500 ms busy timeout. Preserve assignment records and fail on mismatch.

An exclusively created store directory marks initial provisioning. Its survival
allows detection of a lost database. Interrupted initialization requires operator
inspection rather than automatic repair. Complete volume loss requires external
inventory and explicit recovery.

## Alternatives and consequences

SQLx is a valid alternative with async access and migration tooling; it does not
require a connection pool. This slice uses rusqlite because its only database
operation is synchronous startup initialization on one blocking worker.
A configuration file alone cannot provide versioned relational constraints or
transactional identity persistence. External SQLite adds a runtime library
dependency. Pixi can lock that library
as deliberately as Cargo locks bundled SQLite; installation and library loading
need end-to-end validation in #145. Bundling adds a C build but the pinned
Linux Rust environment already includes the compiler and sysroot. Select that
compiler explicitly through target-scoped Pixi activation, without new packages.

SQL migrations live in `apps/agent/migrations/` and are embedded with
`include_str!` so installation needs no loose SQL files. Assess a maintained
migration runner before adding a second schema version rather than growing a
custom migration framework.

The first migration is version 0 to 1 only during fresh creation. Reopening an
existing version 0 store fails because it may represent lost identity. Future
migrations must preserve bindings and add tested upgrade paths. Runtime database
work must introduce a bounded dedicated worker before deployment writes arrive.

## Build portability

Bundling pins SQLite source through Cargo.lock; it does not make an executable
portable between OSes, CPU architectures or libc versions. The selected C
compiler must produce objects compatible with the Rust target and linker.
The Linux C toolchain is a dependency of the conda-forge Rust package, not a
general property of Rust installations. Recheck it when changing that package.

The current Linux x86_64 activation selects the locked native compiler. It does
not establish support for building device binaries on every contributor host.
Prefer native build/test jobs as device targets are introduced. macOS host tools
still use the documented Apple SDK; Linux ARM64 device builds need their own
validated toolchain and tests when that platform is activated.

Cross compilation requires a host-executable C compiler producing target objects,
a matching linker/sysroot and Rust target standard library. Keep this in a
separate build environment for the actual host/target pair. A Pixi host-platform
selector alone cannot describe both ends. Evaluate an existing toolchain or
container-based solution when a concrete delivery needs it; do not maintain a
custom compiler distribution. Release validation must exercise migrations,
restart and failure behavior on the target, and verify runtime library/OS
requirements. Cross-build success or emulation alone is insufficient evidence
of device storage durability.

See the [cc compiler configuration](https://docs.rs/cc/1.11.0/cc/#external-configuration-via-environment-variables),
[Cargo linker configuration](https://doc.rust-lang.org/cargo/reference/config.html#targettriplelinker)
and [conda-forge Rust recipe](https://github.com/conda-forge/rust-feedstock).

## Sources and evidence

Consulted the current [Cargo dependency reference](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html),
[rusqlite API](https://docs.rs/rusqlite/0.41.1/rusqlite/),
[SQLite PRAGMAs](https://www.sqlite.org/pragma.html),
[WAL documentation](https://www.sqlite.org/wal.html) and
[Pixi manifest reference](https://pixi.prefix.dev/latest/reference/pixi_manifest/).
The configuration uses existing Cargo feature syntax and Pixi 0.83.0 target
activation. [Delivery evidence](../journal/2026-11-04-agent-storage.md) records
actual validation. Revisit ownership when runtime database requests appear,
or settings when supported storage demonstrates different durability needs.
