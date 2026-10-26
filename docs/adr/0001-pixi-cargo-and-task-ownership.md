# ADR 0001 — Pixi, Cargo, and task ownership

- **Status:** Accepted.
- **Date:** 2026-10-19
- **Updated:** 2026-10-26
- **Requirement:** [MVP-01](../product/requirements.md#mvp-01--engineering-foundation)

## Context

Contributors need consistent toolchains and language checks. Device workloads
need reproducible runtimes without contributor tooling. Multiple package
managers need clear ownership.

## Decision

Root [pixi.toml](../../pixi.toml) owns tooling and task definitions. The implicit
default feature owns shared tools and build/run/clean; lint owns repository
formatting/linting and contributor setup; test owns tests. The same features'
Linux target tables own device-prefixed aggregates and app/service leaves.
Distinct task names preserve host/device check scope on Linux without separate
device features. Host and device select lint/test alongside default; device
restricts platforms to linux-64. One solve group aligns shared versions.
The [task reference](../guides/tasks.md#pixi-configuration-conventions) owns
configuration conventions. Host validation directly composes focused checks;
Prek combines commit-safety built-ins, a repository-wide fix hook and commit
message validation under [ADR 0007](0007-repository-formatting.md);
device Rust formatting/linting uses rustfmt/Clippy.
Use the
native Rust package, its transitive Linux linker dependencies and explicit
host SDK/linker prerequisites on macOS; avoid redundant activation/compiler packages and virtual-package overrides
without a demonstrated need. Exact dependency pins make upgrades deliberate.
Use the host-installed Pixi executable with a minimum version constraint; CI
pins that minimum to verify compatibility.

The root workspace platform list describes contributor hosts, independently of
managed device runtimes. Use native host build/test/check jobs for contributor
portability. Keep device-only dependencies and integration tasks scoped to
Linux x86_64 in their owning runtime manifests/environments/targets as they are
implemented. A native bootstrap diagnostic build does not imply operational
agent support. The [architecture platform boundary](../architecture/overview.md#developer-hosts-and-device-runtimes)
owns the runtime contract; the [development guide](../guides/development.md#host-prerequisites)
owns current contributor-host limits. Windows contributors use Ubuntu on WSL2,
sharing the Linux toolchain; native Windows builds and their separate tooling
are outside the supported workflow.

Cargo owns Rust dependencies, builds and tests through a virtual workspace.
Inherit shared metadata/lints explicitly, forbid unsafe project code, and use
rustfmt and Clippy without blanket pedantic policies. Extract crates only when
real consumers justify them. The [workspace manifest](../../Cargo.toml) owns
edition, resolver and package defaults.

Prek and Commitizen belong to contributor tooling. Pre-commit checks formatting,
lints and configuration; tests execute separately with all-suite and focused
app/service entry points. Validate contributor tooling and contributor-source
checks on every supported developer host. Keep device-source formatting, lint,
build and tests in the supported device matrix, currently Linux x86_64. Native Pixi target aggregates exclude device checks on other hosts; CI separates contributor and device
jobs and does not start a long-running agent/demo.
Add Ruff/mypy and `pyproject.toml` settings with Python code, frontend tools with
SvelteKit, and other task families only with real workflows. Language formatters
own code layout; shared editor defaults must agree with them.

Git is a host development/CI prerequisite, not an agent runtime requirement.
Each planned ROS workload release owns a separate runtime manifest/lock; the
planned frontend owns its npm lock. Commit relevant locks and validate without
rewriting tracked source or resolution. Explicit format/fix commands may edit
source. Ordinary clean/shutdown preserves operational state; reset is separate.

Pixi resolves, locks and installs environments. FleetForge owns desired state,
authorization, supervision, health, activation/recovery and future artifact
transfer/cache policy. Pixi does not supply fleet coordination or atomic process
switching. Evaluate pixi-pack only when packaging needs justify it.
The [release specification](../specs/releases.md#inputs-installed-environments-and-offline-preparation)
owns the distinction between signed immutable release inputs, provisioned package
bytes and generated release-specific environments. Actual offline cache and ROS
compatibility evidence belongs to the M1 workload/cache deliveries.

## Alternatives and consequences

Host-managed tools make setup depend on machine configuration. A single
contributor/runtime environment leaks development dependencies into workloads.
Independent CI commands duplicate task definitions. Pixi adds a tool to learn,
but keeps environment inputs and task routing reproducible and inspectable.

Rust bundles test, formatting and lint tools; feature ownership need not add
redundant packages. Separate language environments/features require a real
composition need. Use platform defaults until demonstrated host/dependency needs
justify overrides. Current commands and constraints belong to the
[development guide](../guides/development.md) and [task reference](../guides/tasks.md).

## Evidence and revisit conditions

The [toolchain experiment](../experiments/0001-pixi-toolchain.md) owns observed
versions, clean builds and lock-drift/lint failure evidence. The
[contributor platform journal](../journal/2026-10-23-developer-host-platforms.md)
records multi-platform resolution, host prerequisites and native execution
limits. Official
[Pixi environments](https://pixi.prefix.dev/latest/workspace/multi_environment/),
[locked installation](https://pixi.prefix.dev/latest/reference/cli/pixi/install/)
and [Cargo workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html)
describe the mechanisms.

Revisit package/version/routing choices when clean validation fails, Pixi changes
lock/activation behavior, or implemented components have different requirements.
