# Development toolchain

Start with the [README quick start](../../README.md#current-state) to clone and
run the current diagnostic. For the contribution process, see
[CONTRIBUTING.md](../../CONTRIBUTING.md). This guide covers work inside a checkout.

## Host prerequisites

The [README](../../README.md#current-state) owns the supported host and minimum
setup. Keep Git and Pixi on `PATH`, including when Git invokes local hooks.
Docker is optional for reproducing the
[clean-container evidence](../experiments/0001-pixi-toolchain.md).
The root toolchain supports development/builds; it does not establish an agent
deployment or ROS runtime support matrix.

## Install and inspect

From the repository root:

```sh
pixi install --locked -e dev
pixi install --locked
```

`default` builds/runs the application; `dev` adds contributor checks and tools.
The [Pixi manifest](../../pixi.toml) owns exact versions, features and task
routing; [ADR 0001](../adr/0001-pixi-cargo-and-task-ownership.md) explains those
boundaries. Use explicit `-e dev` for checks and Pixi-provided tools to avoid
accidentally resolving undeclared host executables through `PATH`.

## Build and inspect the bootstrap package

```sh
pixi run --locked -e dev check
pixi run --locked -e dev test
pixi run --locked build
```

Run both `check` and `test`: checks inspect formatting, lints and hook
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

Install the hooks once per clone, then check the working tree:

```sh
pixi run --locked -e dev hooks-install
pixi run --locked -e dev hooks-check
```

[prek.toml](../../prek.toml) configures pre-commit source checks and commit-msg
validation; tests run separately. See the
[task reference](tasks.md#hooks-and-commit-messages) for installation caveats,
staged-content behavior and manual message checks. Follow the
[commit convention](../working-agreement.md#review-commits-and-publication).

## PR checks

The [workflow](../../.github/workflows/pr-checks.yml) owns the runner, pinned
actions/tools, permissions and job setup. Every PR to `main`, including docs-only
changes, runs **PR checks / Repository checks**. Fork runs may require maintainer
approval; failures appear in the step logs.

To reproduce its checks locally, install both environments above and set
`PR_BASE` and `PR_HEAD` to the actual base and proposed head commit IDs:

```sh
pixi run --locked -e dev commit-check-range "$PR_BASE..$PR_HEAD"
pixi run --locked -e dev hooks-check
pixi run --locked -e dev test
pixi run --locked build
```

Commit validation needs a nonempty range and sufficient Git history. CI checks
proposed commit messages but validates source using GitHub's merge checkout;
a local branch check does not establish that the merge passes. CI also rejects
tracked-file/index changes after checks. For required-check and review guidance,
see [CONTRIBUTING.md](../../CONTRIBUTING.md#pr-checks-and-maintainer-review).

## Locks and deliberate upgrades

Commit both [pixi.lock](../../pixi.lock) (tools/system dependencies) and
[Cargo.lock](../../Cargo.lock) (Rust dependencies). Neither supplies the host
kernel/glibc, Pixi executable or CA store. Use `pixi --locked` for ordinary
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
`pixi run --locked -e dev cargo generate-lockfile` or a targeted
`cargo update -p <package>` through that environment.

Review the complete lock diff and host/linker compatibility. Rerun checks,
tests, builds and the clean-container walkthrough after toolchain changes;
record versions, source revision, results and limits in a journal. Validate a
new Pixi version before changing its manifest constraint. Consult the current
[Pixi CLI reference](https://pixi.prefix.dev/latest/reference/cli/pixi/) and
[Cargo reference](https://doc.rust-lang.org/cargo/reference/) for tool options.
