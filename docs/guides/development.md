# Development toolchain

The root [Pixi manifest](../../pixi.toml) provisions the Rust and contributor
toolchain. [ADR 0001](../adr/0001-pixi-cargo-and-task-ownership.md) owns package
manager responsibilities; the [toolchain experiment](../experiments/0001-pixi-toolchain.md)
records versions, clean installation and failure evidence.

## Host prerequisites

Use Linux x86_64. Ubuntu 24.04 is the reference distribution. Install
[Pixi](https://pixi.prefix.dev/latest/installation/)
0.82.x separately; 0.82.0 is the validated bootstrap version and the manifest
rejects other minor versions. A working HTTPS CA certificate store and network
access to conda-forge are required for a fresh installation. Minimal Ubuntu
containers need `ca-certificates`. Git is needed to clone and review changes.
Docker is optional, for reproducing the clean-container experiment.
The cleanup task uses the host's POSIX `sh`.
Installed Git hooks also need Pixi on `PATH`; their entries activate the locked
dev tools explicitly.

No host Rust, rustup, C compiler, Python, prek or Commitizen installation is
required. The host supplies the kernel, glibc and basic Unix shell utilities.
Other distributions, architectures and older glibc versions are unverified.
The root toolchain is for development/building; it does not establish an agent
deployment or ROS runtime support matrix.

## Install and inspect

From the repository root:

```sh
pixi install --locked -e dev
pixi install --locked
pixi run --locked -e dev rustc --version
pixi run --locked -e dev cargo --version
pixi run --locked -e dev cargo fmt --version
pixi run --locked -e dev cargo clippy --version
pixi run --locked -e dev prek --version
pixi run --locked -e dev cz version
```

| Environment | Purpose | Features |
| --- | --- | --- |
| `default` | Build and invoke the application | Default feature: essential Rust build/run tooling |
| `dev` | Daily development and contributor checks | Default feature plus `test` and `lint`; adds prek and Commitizen |

Commands without `-e` normally use `default`. Use `-e dev` for development
validation. Both environments share the `toolchain` solve group, keeping shared
package versions identical. Default is declared explicitly only to assign that
group; dev automatically inherits the default feature's dependencies and tasks.
There is no separate `build` environment. The task reference owns
[feature/task composition](tasks.md#feature-and-environment-composition).

Test support, rustfmt and Clippy are bundled with the default Rust package.
The `test` feature therefore initially needs only tasks; `lint` owns its tasks
and the additional contributor packages. Unqualified arbitrary commands can
still resolve host executables through `PATH`; use the documented Pixi-provided
tools rather than relying on undeclared host packages.

Git is a host prerequisite used by prek and Commitizen as well as by the
contributor. It is not installed or version-pinned by this workspace.

The pinned `rust` package supplies the compiler, Cargo, rustfmt, Clippy and
matching standard library for the declared platform. On Linux it also supplies
linker configuration and dependencies on the GCC implementation and sysroot.
No separate Rust activation package or direct GCC/sysroot declaration is needed
for this native build. `pixi.lock` fixes their exact versions.

Rust uses a compiler driver to link the executable even when there is no C
source. The sysroot supplies target system headers, libraries and startup objects
used during linking. Use `pixi run` so the package's linker configuration applies.

The manifest's plain `linux-64` platform uses Pixi's default solver baseline
(glibc 2.28). This describes a host capability; Pixi does not replace the host's
C library. The clean experiment verifies Ubuntu 24.04 userspace, not every
system satisfying that baseline.

## Build and inspect the bootstrap package

Use the canonical task interface for routine development:

```sh
pixi run --locked -e dev check
pixi run --locked build
pixi run --locked -e dev format-check
pixi run --locked -e dev lint
pixi run --locked -e dev test
pixi run --locked -e dev agent-test
pixi run --locked agent-run
pixi run --locked agent-run -- --help
pixi run --locked agent-run -- --version
```

`check` aggregates formatting inspection, Clippy and hook configuration
validation. Run `test` separately for all implemented test suites, or
`agent-test` for the agent package alone. Complete local validation runs both
`check` and `test`. The [task reference](tasks.md) owns every task's tools,
scope, environment, mutation and exit behavior, including explicit `format`/`fix`
commands, agent invocation and safe generated-build cleanup. `agent-run`
builds as needed and forwards arguments after `--` to the executable. Run
build/run tasks in default and checking tasks in dev. Underlying tool commands
are listed in the task reference.

The bootstrap diagnostic prints its compiled package version and platform:
`fleetforge-agent 0.1.0 (x86_64-linux; bootstrap diagnostic)`.

The executable accepts either no arguments or one of the following options:

| Invocation | Standard output | Exit code |
| --- | --- | --- |
| `fleetforge-agent` | Package version and compiled architecture/OS as above | 0 |
| `fleetforge-agent --help` | Usage, default behavior and supported options | 0 |
| `fleetforge-agent --version` | `fleetforge-agent 0.1.0` | 0 |
| Unsupported or extra argument | Empty; stderr identifies the unexpected argument and points to `--help` | 2 |
| Output write or flush failure | May be partial; stderr reports the I/O error when writable | 1 |

Successful invocations leave stderr empty. Options cannot be combined or
repeated. The diagnostic exits after printing; it starts no operational agent.
The `--` in the examples passes the following arguments to the executable
through Cargo. Cargo itself can also print build/run progress on stderr.
The integration tests invoke the built executable directly and assert output,
stderr and exit status for successful commands and invalid inputs, including
non-UTF-8 arguments on Unix.
Output failures, including a closed stdout pipe, return 1 without panicking.
If stderr also fails, the exit status still signals failure. Regression tests
cover closed pipes on Unix and failing stdout/stderr with Linux `/dev/full`.

The virtual Cargo workspace uses edition 2024, resolver 3 and one package at
`apps/agent`. Package metadata and lints are explicitly inherited; unsafe code
is forbidden and standard Clippy lints are enabled. Packages are unpublished
(`publish = false`); licensing is owned by #8.

Builds write to ignored `target/` and environments to ignored `.pixi/`.
Cargo uses its normal user cache (`CARGO_HOME`, otherwise `~/.cargo`).
Native Cargo output is under `target/debug/` or `target/release/`;
`cargo run` locates it automatically.
Checks can create these outputs but must preserve tracked source and lockfiles.
Formatting checks above only inspect files; `cargo fmt --all` rewrites source.

## Local hooks and commit validation

After installing `dev`, install both local Git hook stages and run the checks:

```sh
pixi run --locked -e dev hooks-install
pixi run --locked -e dev hooks-check
```

These install the pre-commit and commit-msg stages, then run the source checks.
The [task reference](tasks.md#hooks-and-commit-messages) owns hook scope,
installation behavior, staged-content handling and manual message/history
commands. Follow the [commit-writing convention](../working-agreement.md#review-commits-and-publication)
when preparing commits.

## PR checks

[PR checks](../../.github/workflows/pr-checks.yml) runs for PRs targeting `main`,
including documentation-only changes. One **Repository checks** job uses the
hosted Ubuntu 24.04 x86_64 runner and Pixi 0.82.1. Actions use full commit-SHA
pins; the workflow grants only `contents: read` and does not persist checkout
credentials. Fork workflows may need maintainer approval to run.

Setup installs the locked `dev` and `default` environments with caching disabled.
The job then runs the canonical tasks:

```sh
pixi run --locked -e dev commit-check-range "$PR_BASE..$PR_HEAD"
pixi run --locked -e dev hooks-check
pixi run --locked -e dev test
pixi run --locked build
```

`hooks-check` runs formatting, Clippy and hook-configuration checks through
`check`; it does not execute tests. The separate `test` and `build` tasks
exercise the workspace tests and the default build environment.

Full checkout history supports commit validation from the event's base SHA to
its proposed head SHA. This includes proposed side-branch commits and uses the
existing `Merge ` message exemption for real merge commits. Source checks use
GitHub's merge checkout; its synthetic merge message is outside that range.
PRs have an existing base, so root-commit handling is unnecessary here.

After validation, `git diff --exit-code` and `git diff --cached --exit-code`
reject tracked changes to source, configuration or locks, including index
changes. This step also runs after failures when checkout succeeded. Ignored
build/environment outputs are expected. GitHub's normal step logs contain
command output and failure diffs; there is no separate diagnostic artifact.
Superseded runs are cancelled and jobs have a 30-minute timeout.

For local reproduction, install both locked environments, set `PR_BASE` and
`PR_HEAD` to an explicit nonempty PR revision range, and run the commands above.
The [delivery journal](../journal/2026-10-22-github-actions.md) records local
success/failure validation and the remaining hosted-run verification. See the
[contribution policy](../../CONTRIBUTING.md#pr-checks-and-maintainer-review)
for recommended required checks and maintainer review.

## Locks and deliberate upgrades

Keep both `pixi.lock` and `Cargo.lock` in Git. Pixi locks the complete tool and
system environment, including package URLs and hashes. Cargo locks Rust package
dependencies; the initial dependency-free executable still has a real Cargo
lockfile. Neither lock covers the host kernel/glibc, Pixi executable or CA store.

Every validation command must use `pixi --locked` at the Pixi command level and
Cargo's `--locked` on commands that resolve Rust packages. Pixi's flag checks
manifest/lock agreement; Cargo's flag independently rejects required Rust lock
updates. `--frozen` on Pixi skips the manifest freshness check and is unsuitable
for validating drift. Cargo's `--frozen` means `--locked --offline`; these are
different meanings. A fresh Pixi install downloads packages; `--locked` does not
imply offline availability. Cargo `--offline` can be added after required crates
are cached (the initial package has no external crates).

For an intentional upgrade, edit the relevant exact version pins in
`pixi.toml`, then resolve and install:

```sh
pixi lock
pixi install --locked --all
```

For a Rust upgrade, update `rust` and the workspace `rust-version`
together. Review the complete lock diff, compiler/formatter/Clippy behavior,
linker and host requirements. For a transitive package refresh within existing
pins, use `pixi update`; `pixi lock` can retain already-satisfying resolutions.
For intentional Rust dependency changes, edit the owning Cargo manifest and
run `pixi run --locked -e dev cargo generate-lockfile` (or a targeted
`cargo update -p <package>`). Review and retain its resulting lock diff.

Rerun the locked build/lint/format commands and the clean-container experiment
after toolchain changes. Record versions, source revision and results with the
delivery. Update the Pixi version constraint only after validating the new
version. Ordinary installation/checks must never regenerate locks silently.
