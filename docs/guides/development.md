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

No host Rust, rustup, C compiler, Python, prek or Commitizen installation is
required. The host supplies the kernel, glibc and basic Unix shell utilities.
Other distributions, architectures and older glibc versions are unverified.
The root toolchain is for development/building; it does not establish an agent
deployment or ROS runtime support matrix.

## Install and inspect

From the repository root:

```sh
pixi install --locked -e dev
pixi install --locked -e build
pixi run --locked -e dev rustc --version
pixi run --locked -e dev cargo --version
pixi run --locked -e dev cargo fmt --version
pixi run --locked -e dev cargo clippy --version
pixi run --locked -e dev prek --version
pixi run --locked -e dev cz version
```

| Environment | Purpose | Features |
| --- | --- | --- |
| `dev` | Daily development and contributor checks | Rust plus prek and Commitizen |
| `build` | Compile and link without installing contributor checks | Rust |

Select an environment explicitly with `-e dev` or `-e build`. Both share the
`toolchain` solve group, keeping shared package versions identical. Neither
inherits the implicit default feature. Pixi's implicit `default` environment is
empty; it is not another supported toolchain environment. Unqualified arbitrary
commands can still resolve host executables through `PATH`, so always use the
explicit environment for Cargo commands. Future canonical tasks can select their
own environment. There is no planned dev/default divergence or duplicated toolset.

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

```sh
pixi run --locked -e build cargo build --workspace --locked
pixi run --locked -e build cargo run --locked -p fleetforge-agent
pixi run --locked -e build cargo run --locked -p fleetforge-agent -- --help
pixi run --locked -e build cargo run --locked -p fleetforge-agent -- --version
pixi run --locked -e dev cargo test --workspace --locked
pixi run --locked -e dev cargo fmt --all -- --check
pixi run --locked -e dev cargo clippy --workspace --all-targets --locked -- -D warnings
```

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
