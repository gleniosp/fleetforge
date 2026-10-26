# FleetForge

**Local-first, Pixi-native robot software lifecycle management.**

> [!WARNING]
> Heavy development: interfaces and setup may change, and things may break.
> The [roadmap](docs/roadmap.md) is only partly implemented; see
> [Current state](#current-state) for what works today.

An operator declares which software a robot should run. A Rust/Tokio agent on
each managed device durably accepts authorized intent, prepares software with
Pixi, supervises the workload, verifies health, and owns local recovery.
Accepted work can finish or recover without the authority when trusted inputs
and resources are local. A reachable local authority can issue new deployments
without public internet.

> [!TIP]
> **Follow the software from release to robot.**
> The [illustrated walkthrough](docs/guides/releases-explained.md) explains the
> planned flow step by step: creating and approving a release, requesting a
> deployment, preparing its environment, running it, checking health, and recovering
> from failure. It introduces the concepts as they appear, with connected examples.

## Current state

FleetForge currently provides a Rust bootstrap diagnostic, a locked build/check
toolchain and unsigned headless ROS 2 Jazzy A/B workload fixtures. The
[workload demonstration](examples/ros-workloads/README.md) verifies real ROS
behavior and isolated health on Linux x86_64. Fleet operation is not implemented
yet.

Develop on **Linux (x86_64/ARM64), Apple Silicon macOS, or Windows through WSL2**.
Device apps and their runtimes currently target **Linux x86_64 (`linux-64`)**;
**Linux ARM64 (`linux-aarch64`) is the next planned device platform**.
See [host prerequisites](docs/guides/development.md#host-prerequisites) for
installation and verification limits. Then:

```sh
git clone https://github.com/gleniosp/fleetforge.git
cd fleetforge
pixi run --locked -e host setup
```

On Linux x86_64, try the current device diagnostic:

```sh
pixi run --locked -e device agent-run
pixi run --locked -e device agent-run -- --help
pixi run --locked -e device agent-run -- --version
```

It prints `fleetforge-agent 0.1.0 (x86_64-linux; bootstrap diagnostic)` and exits.

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
[glossary](docs/product/glossary.md), [requirements](docs/product/requirements.md), and
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
