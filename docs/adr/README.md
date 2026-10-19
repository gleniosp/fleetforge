# Architecture decisions

ADRs own significant choices and their consequences. Acceptance records design
intent; implementation and verification need separate evidence. Amend or supersede
a decision explicitly when the contract changes, updating requirements,
architecture, tests, and GitHub work together.

| ADR | Decision |
| --- | --- |
| [0001](0001-pixi-cargo-and-task-ownership.md) | Pixi/Cargo ownership, environment separation, and canonical tasks |
| [0002](0002-local-first-mvp-boundaries.md) | Local-first authority, release boundary, persistence, and recovery invariants |
| [0003](0003-bounded-decisions-and-evidence.md) | Bounded experiments and evidence-based capability claims |

Networking, descriptor schemas, database settings, process activation, and event
contracts receive their own decisions/specifications when implementation and
experiments establish those boundaries. The [architecture](../architecture/overview.md)
identifies proposed defaults and their owning issues.
