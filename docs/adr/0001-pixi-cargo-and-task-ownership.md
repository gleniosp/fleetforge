# ADR 0001 — Pixi, Cargo, and task ownership

- **Status:** Accepted.
- **Date:** 2026-10-19
- **Updated:** 2026-10-23
- **Requirement:** [MVP-01](../product/requirements.md#mvp-01--engineering-foundation)

## Context

Contributors need consistent toolchains and language checks. Device workloads
need reproducible runtimes without contributor tooling. Multiple package
managers need clear ownership.

## Decision

Root [pixi.toml](../../pixi.toml) owns tooling and task definitions. Its default
feature/environment provides essential build/run tools; `dev` inherits default
and composes `test` and `lint`. One solve group aligns shared versions. Use the
native Rust package and its transitive linker dependencies for Linux x86_64;
avoid redundant activation/compiler packages and virtual-package overrides
without a demonstrated need. Exact pins make upgrades deliberate.

Cargo owns Rust dependencies, builds and tests through a virtual workspace.
Inherit shared metadata/lints explicitly, forbid unsafe project code, and use
rustfmt and Clippy without blanket pedantic policies. Extract crates only when
real consumers justify them. The [workspace manifest](../../Cargo.toml) owns
edition, resolver and package defaults.

Prek and Commitizen belong to contributor tooling. Pre-commit checks formatting,
lints and configuration; tests execute separately with all-suite and focused
app/service entry points. CI checks, tests, builds and validates commit ranges.
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
versions, clean builds and lock-drift/lint failure evidence. Official
[Pixi environments](https://pixi.prefix.dev/latest/workspace/multi_environment/),
[locked installation](https://pixi.prefix.dev/latest/reference/cli/pixi/install/)
and [Cargo workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html)
describe the mechanisms.

Revisit package/version/routing choices when clean validation fails, Pixi changes
lock/activation behavior, or implemented components have different requirements.
