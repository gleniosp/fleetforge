# Development toolchain

This guide covers host prerequisites and contributor setup inside a checkout.
For contribution policy, see [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Host prerequisites

Use host-installed Git and Pixi 0.83+ on `PATH`, including when hooks run.
Fresh installs need HTTPS access to GitHub and the configured package channels.
CI pins Pixi 0.83.0 to verify the minimum supported version.

| Developer host                 | Pixi platform                | Prerequisites outside Pixi                                          |
| ------------------------------ | ---------------------------- | ------------------------------------------------------------------- |
| Linux x86_64 / ARM64           | `linux-64` / `linux-aarch64` | glibc 2.28+, Git, shell utilities and current HTTPS CA certificates |
| Apple Silicon macOS            | `osx-arm64`                  | macOS 13+, Xcode Command Line Tools (Git, linker and SDK)           |
| Windows through Ubuntu on WSL2 | matching Linux platform      | WSL2/Ubuntu plus the Linux prerequisites                            |

On Ubuntu (including Ubuntu inside WSL2):

```sh
sudo apt update
sudo apt install git curl ca-certificates
```

This follows Ubuntu's [APT guidance](https://documentation.ubuntu.com/server/how-to/software/package-management/).
It installs/upgrades the named host packages; a host Rust/C compiler is not
needed because the pinned Linux Rust package brings its linker/sysroot.

On Apple Silicon macOS:

```sh
xcode-select --install
```

Complete [Apple's installation dialog](https://developer.apple.com/documentation/xcode/installing-the-command-line-tools/).
The pinned macOS Rust package supplies Rust and its standard library, not
Apple's linker/SDK. Keep macOS and Command Line Tools updated through Software
Update. No separate Homebrew installation is required.

Then install Pixi using its [official installer](https://pixi.prefix.dev/latest/installation/)
if it is not already on `PATH`:

```sh
curl -fsSL https://pixi.sh/install.sh | sh
```

On Windows, [install WSL2 with Ubuntu](https://learn.microsoft.com/en-us/windows/wsl/install),
then follow the Ubuntu steps inside WSL. Keep the checkout in the Linux
filesystem, such as `~/fleetforge`, per [Microsoft's guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems).
Native Windows and Intel macOS are outside the supported developer matrix.

Keep the host OS, certificate stores and download tools updated.

Three native developer platforms resolve in the lock and have CI definitions;
only Linux x86_64 execution has been checked locally. Native ARM64/macOS CI and
WSL-specific integration remain unverified until actual results exist. Device
support follows the separate [architecture contract](../architecture/overview.md#developer-hosts-and-device-runtimes).
Docker is optional for the [Ubuntu experiment](../experiments/0001-pixi-toolchain.md).
Keep Docker updated through its [installation source](https://docs.docker.com/engine/install/ubuntu/#upgrade-docker-engine).
When refreshing experiment prerequisites, rebuild with `docker build --pull --no-cache`;
the pinned base-image digest remains an explicit reviewed input.

## Install and inspect

After installing the host prerequisites above, run once per clone:

```sh
pixi run --locked -e host setup
```

Pixi installs the required host environment before the task runs; `setup` then
preloads the checksum-pinned dprint Wasm plugin and installs the pre-commit and
commit-msg hooks. Rerun it after moving the checkout
or recreating the environment. It does not install host Git, Pixi or platform
SDKs. Other `pixi run --locked` tasks also install their required environment
automatically; hooks still need this explicit per-clone setup. To install the
environments without installing hooks, use `pixi install --locked --all`, then
`pixi run --locked -e host format-setup` to preload the formatter plugin.

The [task reference](tasks.md) explains environment selection and task scopes;
the [manifest](../../pixi.toml) owns exact commands and pins.

## Build and inspect the bootstrap package

```sh
pixi run --locked -e host check
# Linux x86_64 device validation:
pixi run --locked -e device device-check
pixi run --locked -e device device-test
pixi run --locked -e device device-build
```

In the device environment on Linux x86_64, run both `device-check` and
`device-test`: checks inspect Rust formatting and lints; tests execute the agent
suite and bounded real ROS A/B fixtures separately. The ROS fixture installs
independent runtime copies and needs package access or an existing cache. Its
[guide](../../examples/ros-workloads/README.md) provides the focused command and
Ubuntu 24.04 reference-container invocation. The [task reference](tasks.md) lists
focused checks, deliberate formatting/fixes and cleanup. Build output is ignored
under `target/`, environments under `.pixi/`; Cargo also uses its user cache.
Non-mutating checks must preserve tracked source and all lockfiles.

The [bootstrap CLI](../../apps/agent/src/main.rs) prints and exits; it does not
start an operational agent. The README shows its supported invocations.
Unsupported or extra arguments return 2; output failures return 1. Successful
invocations return 0 with empty executable stderr, though Cargo may print
build/run progress there. [CLI tests](../../apps/agent/tests/cli.rs) own detailed
output and failure expectations.

## Repository formatting

```sh
pixi run --locked -e host fix
pixi run --locked -e host check
```

`fix` composes the current host fixes (`format`). `format` rewrites eligible
documents/configuration, including untracked files;
review the resulting diff before handoff. `format-check` checks the same scope
without writing. Both accept optional file/directory paths. `check` directly
composes `format-check` and hook-configuration validation,
without running Prek hooks. It covers eligible working-tree files, including
untracked files. Add component lint checks/fixes to these aggregates only when
their owning code arrives. Contributors and agents should format, check and
review their changes before handing them off.

[dprint.json](../../dprint.json) owns Markdown, JSON/JSONC, YAML and TOML
selection, exclusions and layout. One versioned, SHA-256-pinned Oxc Wasm plugin
provides these formatters; no Node/npm or separate Oxfmt installation is needed.
The executable is locked through Pixi; plugin bytes are separately pinned in
the dprint configuration and cached by dprint. Initial setup needs network
access to the package channel and GitHub plugin release. Warm-cache formatting
needs those inputs available locally. To upgrade, deliberately update the
executable pin/lock or plugin URL/checksum, then rerun setup and validation.

The pinned plugin defaults supply two-space indentation, LF/final newline and
preserved prose wrapping. Its configuration disables embedded-code formatting
without adding configuration for absent languages. Dependency locks and
generated output are excluded. Readable release-fixture JSON is formatted; its
payload strings and encoded canonical vectors retain their decoded values.
Canonical `release.json` descriptors are excluded by filename, and Git attributes
disable text/newline conversion for them. This protects exact bytes; it does not
validate JCS encoding. Additional signed/canonical inputs need explicit protection
with their owning delivery. Ordinary pretty printing changes exact bytes even
when property order is retained.
Review Markdown tables, hard breaks, examples and meaningful string contents.

[EditorConfig](../../.editorconfig) applies only to listed fallback files without
a dedicated formatter: plain text, shell/Docker inputs and miscellaneous text
configuration. It does not compete with dprint, Rust's device-scoped rustfmt or
#12's Python owner. Add newly introduced fallback formats explicitly. dprint
does not read EditorConfig; formatted output is shared across editor/CLI, while
indentation during typing and file-encoding preferences remain editor behaviours.

### Editor integration

Open the repository root as the workspace and run setup first. The committed
[extension recommendations](../../.vscode/extensions.json) select dprint,
EditorConfig, rust-analyzer and CodeLLDB, plus the optional Oxc recommendation.
[VS Code settings](../../.vscode/settings.json)
route supported document/configuration saves to
`./.pixi/envs/host/bin/dprint`; the same project configuration/plugin serves
CLI and editor. Stable formatting is enabled to match the CLI's default passes.
No indentation/newline/layout options are duplicated in VS Code settings.

Other editors can use the same executable with `dprint lsp` or their dprint
integration. The canonical CLI commands remain the fallback. Rust editor tools
need the locked Rust toolchain on their environment's `PATH`; launching a fresh
editor process from the host environment can supply it. Extension recommendations
do not install another compiler or expand managed-device support. One-off
validation of CLI/editor-service consistency and hooks is recorded in
the [delivery journal](../journal/2026-10-26-repository-formatting.md); no
formatter-specific regression suite is installed.

## Local hooks and commit validation

The setup task above installs hooks. To check the working tree:

```sh
pixi run --locked -e host check
```

[prek.toml](../../prek.toml) configures pre-commit formatting/checks and commit-msg
validation; tests run separately. See the
[task reference](tasks.md#hooks-and-commit-messages) for installation caveats,
staged-content behavior and manual message checks. Follow the
[commit convention](../working-agreement.md#review-commits-and-publication).

## PR checks

The [workflow](../../.github/workflows/pr-checks.yml) runs contributor setup,
direct host checks and commit validation on all three native hosts. A separate
Prek invocation skips `fix` and runs only the three commit-safety built-ins: case
conflicts, merge conflicts and large added files.
The Linux-only `device` job uses device-prefixed tasks to format/lint, build
and test the agent plus the bounded real ROS A/B fixture. Repository `check` directly composes focused checks; it never invokes the hook
runner. Agent Rust checks
stay in the device job. The
aggregate **Repository checks** requires both scopes; CI does not start a
long-running agent or fleet demo. ROS fixture processes exit after their bounded
checks. Fork runs may need maintainer approval.

Reproduce the scopes locally, supplying actual commit IDs for the range:

```sh
pixi run --locked -e host check
pixi run --locked -e host commit-check-range "$PR_BASE..$PR_HEAD"
# Linux x86_64 only:
pixi run --locked -e device device-check
pixi run --locked -e device device-test
pixi run --locked -e device device-build
```

Commit validation needs a nonempty range and sufficient Git history. CI checks
proposed commit messages but validates source using GitHub's merge checkout;
a local branch check does not establish that the merge passes. CI also rejects
tracked-file/index changes after checks. For required-check and review guidance,
see [CONTRIBUTING.md](../../CONTRIBUTING.md#pr-checks-and-maintainer-review).

## Locks and deliberate upgrades

Commit [pixi.lock](../../pixi.lock) (tools/system dependencies),
[Cargo.lock](../../Cargo.lock) (Rust dependencies), and each
[workload release's](../../examples/ros-workloads/README.md) independent
manifest/lock. These do not supply the host
kernel/glibc, platform SDK/linker, Pixi executable or CA store. Use `pixi --locked`
for ordinary
installation/validation and Cargo's `--locked` for dependency-resolving commands;
they independently reject required lock updates. Pixi's `--frozen` skips the
manifest freshness check, so it is unsuitable for validating drift. Locked does
not mean offline: fresh installs need package bytes.

For an intentional tool upgrade, edit the exact pins in `pixi.toml`, then run:

```sh
pixi lock
pixi install --locked --all
```

Use `pixi update` for a deliberate transitive refresh within existing pins;
`pixi lock` may retain satisfying resolutions. For Rust upgrades, update the
workspace `rust-version` with the toolchain pin. For Rust dependency changes,
edit the owning Cargo manifest and run
`pixi run --locked -e host cargo generate-lockfile` or a targeted
`cargo update -p <package>` through that environment.

Review the complete lock diff and host/linker compatibility. Rerun checks,
tests, builds and the clean-container walkthrough after toolchain changes;
record versions, source revision, results and limits in a journal. Validate a
new Pixi version before changing its manifest constraint. Consult the current
[Pixi CLI reference](https://pixi.prefix.dev/latest/reference/cli/pixi/) and
[Cargo reference](https://doc.rust-lang.org/cargo/reference/) for tool options.
