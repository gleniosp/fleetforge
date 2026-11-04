# ADR 0009 — Pixi-delivered agent environments

- **Status:** Accepted direction; runtime adoption awaits #145 evidence.
- **Date:** 2026-11-04
- **Delivery:** [#16](https://github.com/gleniosp/fleetforge/issues/16) records the
  boundary; [M2-06 (#145)](https://github.com/gleniosp/fleetforge/issues/145)
  validates packaging. Native installation/upgrades remain deferred FUT-08.

## Context

FleetForge already uses Pixi to prepare independent workload environments.
The agent also needs reproducible installation and dependency provisioning,
offline startup, stable identity and eventual upgrades on selected devices.
Contributor hosts, installed agent runtimes and managed workloads have different
lifecycles. Native delivery format and production updater tooling were previously
left open.

## Decision

Use a dedicated locked Pixi environment as the intended agent installation unit,
with a prebuilt agent package. Prefer pixi-pack distribution and Pixi-managed
SQLite, gated by a bounded reference Linux x86_64 experiment. Keep #16's tested
bundled SQLite implementation until that path is validated and adopted.

The [agent delivery contract](../architecture/agent-delivery.md) owns installation,
service/updater responsibilities, persistent state, compatibility, platform
evidence and delivery sequencing. Ordinary startup uses an installed environment.
No device compiler, startup solve or network dependency is introduced.

First validate explicit installation commands. Later select service integration
and compare maintained update engines with a narrowly scoped updater before
introducing autonomous upgrades. Ansible is a provisioning candidate, not a
requirement. Tooling itself needs versioning and an update owner; it can share
FleetForge releases without being replaced through the failing agent environment.

## Alternatives and consequences

A standalone executable with bundled SQLite minimizes runtime dependencies and
remains the working baseline. A dedicated Pixi runtime can pin external SQLite
just as deliberately, centralizes dependency installation and aligns with
workload delivery tooling, but requires reliable environment/library activation
and retained offline recovery inputs.

An OS package may still provide bootstrap/service tooling around the Pixi
runtime. Containers remain the MVP simulation boundary, not a claim of native
device support. Ansible can repeat provisioning but does not establish local
crash recovery. An established update framework may reduce custom update logic;
its platform integration and SQLite/schema recovery still need evidence.
Mender application Update Modules are one candidate for that comparison.
Image updaters such as RAUC become relevant if the project owns complete device
OS images and boot integration; they are not prerequisites for the agent package.

Reusing compiler components already provided by the locked Linux Rust package
avoids redundant tooling today. Explicit Clang or a cross toolchain is a separate
build decision requiring a target need. Packages/bundles remain platform-specific,
and native runtime checks remain necessary.

## Validation and revisit conditions

#145 must prove real packaged execution with external SQLite, offline unpacking,
noninteractive startup, platform rejection, persistence failures and switching
compatible environments. It must record pinned Pixi/pack tooling versions,
sources, licenses and limits under [ADR 0003](0003-bounded-decisions-and-evidence.md).
If blocked, retain the baseline, preserve the reproducer and resolve the
successor contract explicitly. Do not relabel this accepted direction as verified.

Consulted [Pixi pack documentation](https://pixi.prefix.dev/latest/deployment/pixi_pack/),
[pixi-pack upstream](https://github.com/Quantco/pixi-pack),
[Pixi run behavior](https://pixi.prefix.dev/latest/reference/cli/pixi/run/),
[Ansible service management](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/systemd_service_module.html)
and [Mender update modules](https://docs.mender.io/artifact-creation/create-a-custom-update-module)
and [RAUC basics](https://rauc.readthedocs.io/en/latest/basic.html).
Current #16 configuration remains compatible with project Pixi 0.83.0; no pack
tool/backend compatibility or operational platform expansion has been claimed.
Revisit when the packaging experiment, target-platform constraints or updater
failure evidence contradict the intended model.
