# Agent delivery, installation and upgrades

**Status:** Accepted intended architecture; packaging, shared SQLite and native
installation are not yet verified. [ADR 0009](../adr/0009-pixi-agent-delivery.md)
records the decision. The current implementation remains the source-built
Linux x86_64 agent with bundled SQLite described by [ADR 0008](../adr/0008-agent-sqlite-storage.md).

## Installation unit and ownership

Deliver a prebuilt agent package in its own versioned, locked Pixi runtime
environment. Prefer pixi-pack for offline environment distribution, subject to
[#145](https://github.com/gleniosp/fleetforge/issues/145) validation. Pixi-provided
SQLite is the intended candidate dependency; retain bundled SQLite until its
replacement passes that gate.

Build Rust/C code in CI or the development build environment. Installed devices
receive runtime packages, not contributor toolchains. The root repository
`device` environment is a development/test environment, not the installed agent
runtime. Agent environments and managed workload release environments have
separate manifests, locks, permissions and update ownership.

| Owner                 | Responsibility                                                                                     |
| --------------------- | -------------------------------------------------------------------------------------------------- |
| Pixi                  | Resolve/install locked environments for the agent and, separately, workloads                       |
| pixi-pack/pixi-unpack | Package and reconstruct the selected runtime from local distribution inputs                        |
| Installer             | Provision protected paths/users/configuration, verify artifacts and prepare installed environments |
| OS service manager    | Boot startup, process supervision, shutdown and bounded restart policy                             |
| Agent updater         | Stage/select versions, check compatibility, verify readiness and retain recovery information       |
| FleetForge agent      | Drive Pixi preparation for managed workload releases and own their execution/recovery              |

Ansible is a candidate for administrator-driven provisioning of reachable
devices; it can invoke installation and service configuration. It is not required
for normal agent execution. Select it only when repeatable provisioning provides
a present benefit. systemd is a Linux service-manager candidate; each supported
OS needs an evidenced service integration. Neither tool is selected as a universal
agent updater.

## Startup and persistent state

Prepare the installed environment before normal startup. The launcher must run
it without resolving, downloading or installing packages, including without a
network connection or interactive shell. `pixi run --locked` can still install an
environment and is not by itself proof of this property.

Keep identity/database, credentials, configuration and update progress outside
versioned environments. Workloads must not mutate the agent runtime or its
protected state. Removing an old environment must preserve these records.
Environment activation, shared-library loading, prefix assumptions and recovery
entry points must be tested through the actual installed artifact.

## Updates and recovery

Prepare a candidate environment alongside the current one. Verify its
authenticity/integrity, platform and installer/bundle compatibility before
activation; a lockfile hash alone does not establish publisher authorization.
Preflight schema compatibility, coordinate stopping the agent, select/start the
candidate, verify readiness, then durably record success. Define what happens to
managed children during agent replacement; do not infer uninterrupted workload
supervision from successful environment switching.

Record update progress durably so interruption has a defined next-boot outcome.
Retain the previous environment and a recovery entry point usable when the
agent cannot start. Returning to an older binary is allowed only when it can
read the retained state. Restoring a database backup may discard accepted work
and requires an explicit recovery policy; never blindly reverse schema changes.

Initially validate explicit installation commands. Before autonomous updates,
compare a maintained update engine with a bounded FleetForge-specific updater
and decide external versus self-upgrade ownership in #72. An external recovery
entry point must survive failure of the environment being replaced.

Installer/updater code and service configuration need versioned releases, tests
and compatibility metadata, but may share the FleetForge repository and release
process. Declare supported bundle formats, installer versions and schema ranges.
Choose how installation tooling and Pixi itself are maintained through the device
OS/provisioning lifecycle; avoid assuming they upgrade themselves successfully.

## Platform matrix

Identify OS, CPU architecture, relevant ABI/libc constraints and artifact version
explicitly. Reject incompatible artifacts before activation. Start with Linux
x86_64/Ubuntu 24.04; Linux ARM64 is the first planned device expansion. Other
device operating systems require explicit scope and native integration evidence.
Contributor-host support does not imply operational agent support.

Packing another platform's dependencies does not cross-compile the agent.
Supply a package built for the target, then verify installation, SQLite behavior,
restart and recovery on that target. Separate build/pack/emulation observations
from native execution and storage durability evidence. Use existing locked
compiler components where adequate; add an explicit compiler or cross toolchain
only for a demonstrated target requirement, with matching linker/sysroot.
Bundling SQLite does not remove OS/libc requirements.

## Delivery sequence

[#16](https://github.com/gleniosp/fleetforge/issues/16) owns current identity
persistence. #145 establishes the Linux x86_64 packaging/shared-SQLite path and
layout before [#87](https://github.com/gleniosp/fleetforge/issues/87) uses it for
runtime privileges. A blocked experiment must produce a reproducer and an
explicit accepted layout/fallback decision before dependent work is ready.

[#31](https://github.com/gleniosp/fleetforge/issues/31) and
[#32](https://github.com/gleniosp/fleetforge/issues/32) reuse that artifact for
MVP Compose/provisioning. Native platform selection, installation and boot
supervision remain in deferred #69/#70/#103; production upgrade ownership and
interruption recovery remain in deferred #72/#104. The bounded M2 packaging
task does not activate the rest of FUT-08.
