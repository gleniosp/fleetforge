# FleetForge

**Local-first, Pixi-native robot software lifecycle management.**

> **Heavy development:** FleetForge is under active development. Interfaces,
> setup, and plans may change, and breaking changes are expected. Much of the
> planned functionality is not implemented yet; see [Current state](#current-state)
> for what exists today.

An operator declares which software a robot should run. A Rust/Tokio agent on
each managed device durably accepts authorized intent, prepares software with
Pixi, supervises the workload, verifies health, and owns local recovery.
Accepted work can finish or recover without the authority when trusted inputs
and resources are local. A reachable local authority can issue new deployments
without public internet.

## Current state

The repository provides design contracts and a reproducible development
toolchain. Fleet operation is not implemented yet.

Build and invoke the bootstrap diagnostic from the repository root:

```sh
pixi run --locked agent-run
pixi run --locked agent-run -- --help
pixi run --locked agent-run -- --version
```

See the [development guide](docs/guides/development.md) for prerequisites,
CLI behavior and validation commands.

## Planned MVP

- One local Rust/Tokio authority and three independent device agents with SQLite.
- Separate asset/device identities and tenant/authority/assignment context.
- Real headless ROS 2 Jazzy Python A/B releases in independent Pixi environments.
- Pre-provisioned immutable releases and package bytes for fresh offline installs.
- Device-initiated WebSocket push over TLS 1.3 mutual TLS, registry authorization,
  and Ed25519-signed releases and desired-state instructions.
- Separate preparation, controlled stop/start, actual ROS health, verified recovery,
  and explicit rollback as a new generation.
- A SvelteKit/TypeScript console, bounded diagnostics, and honest observation freshness.
- Docker Compose on Linux x86_64, with Ubuntu 24.04 as the reference container.

MVP authentication, signing, and workload privilege separation are required
design boundaries; production hardening still needs separate evidence. Gazebo,
physical pilots, distributed artifacts, advanced peer networking, multi-tenant
management, and hosted services are deferred. Cloud, brokers, central servers,
and site gateways are optional future choices. Million-device capacity is a
future measured target.

## Read and contribute

Start with the [documentation map](docs/README.md),
[requirements](docs/product/requirements.md), and
[architecture](docs/architecture/overview.md). The [roadmap](docs/roadmap.md)
links to GitHub delivery owners; [traceability](docs/traceability.md) maps
requirements to issues and intended verification. [ADRs](docs/adr/README.md)
explain decisions; [journals](docs/README.md#reading-design-and-evidence) record
factual evidence.

Use an agreed issue for substantial changes and follow the [working
agreement](docs/working-agreement.md), including branch names such as
`docs/85-consolidate-architecture` and normally one PR per issue. The maintainer
owns approval and merge. [CONTRIBUTING.md](CONTRIBUTING.md) is the contributor
entry point; [AGENTS.md](AGENTS.md) routes agent instructions and repository
skills.

## License and community

Copyright 2026 FleetForge contributors. FleetForge's original code,
documentation, and configuration are licensed under the
[Apache License, Version 2.0](LICENSE), unless a file states otherwise.
Third-party materials retain their own licenses; see the
[provenance and distribution guidance](THIRD_PARTY.md).

Read the [security policy](SECURITY.md) before reporting a suspected
vulnerability and the [code of conduct](CODE_OF_CONDUCT.md) for participation
and reporting expectations.
