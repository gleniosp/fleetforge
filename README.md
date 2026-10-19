# FleetForge

**Distributed software deployment and fleet management for robots.**

FleetForge lets an operator declare which software robots should run. Each robot
durably accepts desired state, reconciles it with its actual workload, and owns
deployment, health verification, and recovery locally.

Robots should continue operating and finish or recover from accepted work when
operator connectivity disappears, provided the required release inputs and
resources are available locally.

## Current state

This repository contains the foundation design. The agent, operator, dashboard,
releases, development toolchain, and automated product tests are planned work.
There is no runnable fleet or installation command yet. The initial development
and simulation target is Linux x86-64; platform support requires validation.

## Planned MVP

- Three independent Rust/Tokio agents and one Rust operator authority.
- Two real, immutable Pixi-managed application releases, A and B.
- SQLite state on every robot and on the operator.
- Direct communication, durable generations, and retry-safe reconciliation.
- Staged preparation, supervised processes, real health checks, and recovery.
- Structured logs, bounded durable events, and a SvelteKit operator console.
- Docker Compose simulation and independently tested offline/failure scenarios.

The MVP assumes a trusted local development environment. It is not ready for
untrusted networks or production robots. Artifact transfer, advanced P2P,
ROS 2, multi-tenancy, PostgreSQL, cloud services, and IaC belong to future scope.

## Read and contribute

Start with the [documentation map](docs/README.md),
[product requirements](docs/product/requirements.md), and
[architecture](docs/architecture/overview.md).

The [roadmap](docs/roadmap.md) points to GitHub milestones and issues, which own
active task scope, acceptance checklists, dependencies, and progress. The
[traceability map](docs/traceability.md) connects requirements to planned
components and verification. [ADRs](docs/adr/README.md) record durable decisions;
the [engineering journal](docs/journal/2026-10-19-foundation-design.md) records
what was actually checked and the limits of that evidence.

Development is maintainer-led. Use an agreed
[GitHub issue](https://github.com/gleniosp/fleetforge/issues) before starting a
substantial change. Contribution, licensing, and executable setup files will be
introduced by their bootstrap tasks; this document does not imply they already
exist.
