# Architecture decisions

ADRs explain significant choices, alternatives, consequences and revisit
conditions. Acceptance is design intent; implementation and verification require
separate evidence. Linked architecture contracts own the detailed current
behavior.

| ADR                                                   | Current decision                                                                |
| ----------------------------------------------------- | ------------------------------------------------------------------------------- |
| [0001](0001-pixi-cargo-and-task-ownership.md)         | Pixi/Cargo/tool ownership and Pixi versus FleetForge lifecycle responsibilities |
| [0002](0002-local-first-mvp-boundaries.md)            | Local logical authority, offline execution and crash-recoverable ownership      |
| [0003](0003-bounded-decisions-and-evidence.md)        | Bounded investigation and evidence policy                                       |
| [0004](0004-asset-device-and-tenancy.md)              | Asset/device identity, assignment and tenancy context                           |
| [0005](0005-authenticated-push-transport.md)          | Direct mutually authenticated WebSocket push                                    |
| [0006](0006-signed-trust-and-privilege-boundaries.md) | Signed releases/instructions and MVP privilege/trust boundaries                 |
| [0007](0007-repository-formatting.md)                 | Centralized dprint formatting, fallback EditorConfig and Prek autofixes         |

The [release specification](../specs/releases.md) owns the version 1 descriptor,
signed bytes, schemas and input limits. Instruction encodings, SQLite settings
and supervision mechanisms are specified/validated in their owning slices. They
do not reopen accepted transport/framework/identity choices without demonstrated
need. The [architecture](../architecture/overview.md) links current contracts
and bounded experiments; the [traceability map](../traceability.md) links
delivery owners.
