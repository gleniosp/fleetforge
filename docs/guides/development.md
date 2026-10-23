# Development toolchain

This guide covers host prerequisites and contributor setup inside a checkout.
For contribution policy, see [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Host prerequisites

Use host-installed Git and Pixi 0.83+ on `PATH`, including when hooks run.
Fresh installs need HTTPS access to GitHub and the configured package channels.
CI pins Pixi 0.83.0 to verify the minimum supported version.

| Developer host | Pixi platform | Prerequisites outside Pixi |
| --- | --- | --- |
| Linux x86_64 / ARM64 | `linux-64` / `linux-aarch64` | glibc 2.28+, Git, shell utilities and current HTTPS CA certificates |
| Apple Silicon macOS | `osx-arm64` | macOS 13+, Xcode Command Line Tools (Git, linker and SDK) |
| Windows through Ubuntu on WSL2 | matching Linux platform | WSL2/Ubuntu plus the Linux prerequisites |

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
installs the pre-commit and commit-msg hooks. Rerun it after moving the checkout
or recreating the environment. It does not install host Git, Pixi or platform
SDKs. Other `pixi run --locked` tasks also install their required environment
automatically; hooks still need this explicit per-clone setup. To install the
environments without installing hooks, use `pixi install --locked --all`.

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

In the device environment on Linux x86_64, run both `device-check` and `device-test`: checks inspect formatting, lints and hook
configuration; tests execute separately. The [task reference](tasks.md) lists
focused checks, deliberate formatting/fixes and cleanup. Build output is ignored
under `target/`, environments under `.pixi/`; Cargo also uses its user cache.
Non-mutating checks must preserve tracked source and both lockfiles.

The [bootstrap CLI](../../apps/agent/src/main.rs) prints and exits; it does not
start an operational agent. The README shows its supported invocations.
Unsupported or extra arguments return 2; output failures return 1. Successful
invocations return 0 with empty executable stderr, though Cargo may print
build/run progress there. [CLI tests](../../apps/agent/tests/cli.rs) own detailed
output and failure expectations.

## Local hooks and commit validation

The setup task above installs hooks. To check the working tree:

```sh
pixi run --locked -e host check
```

[prek.toml](../../prek.toml) configures pre-commit source checks and commit-msg
validation; tests run separately. See the
[task reference](tasks.md#hooks-and-commit-messages) for installation caveats,
staged-content behavior and manual message checks. Follow the
[commit convention](../working-agreement.md#review-commits-and-publication).

## PR checks

The [workflow](../../.github/workflows/pr-checks.yml) runs contributor setup,
hooks/configuration and commit validation in `host` on all three native hosts.
The Linux-only `device` job uses device-prefixed tasks to format/lint, build
and test the agent. Repository `check` runs Prek built-ins and validates hook configuration;
agent Rust checks stay in the device job. The
aggregate **Repository checks** requires both scopes; CI does not start a
long-running agent/demo. Fork runs may need maintainer approval.

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

Commit both [pixi.lock](../../pixi.lock) (tools/system dependencies) and
[Cargo.lock](../../Cargo.lock) (Rust dependencies). Neither supplies the host
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
