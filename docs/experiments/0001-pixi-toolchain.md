# Pixi Rust toolchain experiment — 2026-10-21

**Delivery:** [M0-03 / #3](https://github.com/gleniosp/fleetforge/issues/3),
[MVP-01](../product/requirements.md#mvp-01--engineering-foundation).
**Decision:** [ADR 0001](../adr/0001-pixi-cargo-and-task-ownership.md).

## Question and stopping condition

Can native conda-forge Rust provide the compiler, formatter, linter and linker
without host Rust/C tools, while separating contributor checks and rejecting
stale locks without source or lockfile rewrites?

Compare plain `rust` with `rust_linux-64` activation. Stop after fresh locked
installation, path/version checks, real compile/link/run, format/Clippy checks,
and controlled lock/lint failures. Git is a host prerequisite. Product behavior
and canonical tasks belong to their own deliveries.

This check verifies that our manifest, environment boundaries and Cargo commands
work together on the reference host without accidental compiler dependencies.
We rely on Pixi's documented resolution and installation behavior. The separate
experiment record is useful here because package selection was uncertain and
the simpler native Rust package disproved the initial assumption. Routine
locked installs/builds are sufficient after this foundation is established;
repeat the clean check when relevant toolchain or host requirements change.

## Sources and package choice

Consulted the current official [Pixi Rust tutorial](https://pixi.prefix.dev/latest/tutorials/rust/),
[environment documentation](https://pixi.prefix.dev/latest/workspace/multi_environment/),
[install reference](https://pixi.prefix.dev/latest/reference/cli/pixi/install/),
and conda-forge's [Rust recipe](https://github.com/conda-forge/rust-feedstock/blob/main/recipe/recipe.yaml)
and [native linker setup](https://github.com/conda-forge/rust-feedstock/blob/main/recipe/install-rust.sh).
These describe the native toolchain and locked installation mechanisms.

The initial candidate used `rust_linux-64` with direct GCC/sysroot pins,
managed Git, a default/dev mirror and a glibc override. A clean comparison
workspace containing only `rust = "=1.98.1"` built the same Cargo package with
`pixi install` followed by `pixi run --locked cargo build --locked --offline`.
Verbose output confirmed `-C linker=x86_64-conda-linux-gnu-cc` without a host
compiler. The native Rust package already supplies linker setup and its system
dependencies, so the extra declarations were removed. The fixture below
reproduces the selected configuration.

## Setup and inputs

Source: the uncommitted working tree on
`build/3-locked-pixi-cargo-toolchain`, based on
`8492da06dab19c6424842c16a40d6ef03b05a80b`.
Inputs are the root Pixi/Cargo manifests, both locks and the agent package.

Host: Ubuntu 26.04.1 x86_64, kernel `7.0.0-38-generic`, Docker 29.7.2.
The disposable container uses Ubuntu 24.04.5 userspace and glibc 2.39, sharing
that host kernel. The experiment Dockerfile pins the Ubuntu image digest and
installs host Git and HTTPS CA certificates. Apt repositories are live; these
host prerequisites are outside `pixi.lock`.

Pixi 0.82.0 is a separately installed, statically linked executable mounted
read-only at `/usr/local/bin/pixi`. Its SHA-256 is
`1dff1db704884f078c44b4c7fb3c5bc6f946fc3d1fa679edf214ad79187a9c64`.
No host Rust/C compiler, Cargo home, environment or package cache is mounted.
The source mount is read-only; the script copies inputs to a temporary
container directory, disables user/system Pixi config and starts with an empty
container package cache. It rejects pre-existing compilers and contributor
checks, and verifies that Git comes from `/usr/bin/git`.

## Reproduce the final checks

From the repository root, with Pixi 0.82.0 available:

```sh
docker build --tag fleetforge-toolchain-evidence:issue-3 experiments/pixi-toolchain
docker run --rm \
  --mount type=bind,src="$PWD",dst=/source,readonly \
  --mount type=bind,src="$(command -v pixi)",dst=/usr/local/bin/pixi,readonly \
  fleetforge-toolchain-evidence:issue-3 \
  bash /source/experiments/pixi-toolchain/verify.sh
```

The script contains every check and disposable mutation. It must run in the
container: its initial tool-absence checks intentionally reject normal developer
shells. It is an experiment fixture, not the canonical task suite.

## Results

The final run returned exit 0 and:

```text
PASS: fresh installs, isolated tool paths, builds, lock rejection, inherited unsafe lint, source preservation
```

| Check | Observed result |
| --- | --- |
| Fresh locked install | dev/build installed from lock; implicit default has no packages |
| Rust/Cargo | rustc 1.98.1, Cargo 1.98.1 |
| Formatter/linter | rustfmt 1.9.0-stable, Clippy 0.1.98 |
| Transitive native toolchain | GCC implementation 16.2.0, binutils 2.46.1, sysroot 2.28 |
| Isolation | 17 build packages; 54 dev packages; prek 0.5.6 and Commitizen 4.19.2 absent from build |
| Tool paths | Rust tools and linker under each environment's own `bin/`; Git resolves to `/usr/bin/git` |
| Compilation | Both environments compile/link afresh using distinct target directories; release build also succeeds |
| Execution | `fleetforge-agent 0.1.0 (x86_64-linux; bootstrap diagnostic)` |
| Source checks | Formatting and Clippy with warnings denied pass |
| Stale Pixi lock | Pin changed to Rust 1.98.0: locked install and run reject `lock file not up-to-date with the workspace` |
| Stale Cargo lock | Workspace version changed to 0.1.1: locked offline build rejects `cannot update the lock file ... because --locked was passed` |
| Inherited lint | Injected `unsafe {}` rejects with `usage of an unsafe block` and `-F unsafe-code` |
| Mutation checks | Source/lock SHA-256 snapshots match before/after successful checks and each rejection; restoring fixtures reproduces original bytes |

The lock's default Linux virtual packages include glibc 2.28; the manifest has
no custom override. This describes solver assumptions, not an installed host
libc. All 17 build package URLs occur unchanged in dev. Git is absent from the
lock; it is available on the host in both environments.

Final lock SHA-256 values:

```text
a4945d2aaed2193db092c7bb0d12bde5d74a72df5bc4dfb1437ffc82aac976b3  pixi.lock
0bdbd3f77349171917b2f8568c86b123306747a32dd0f9ae7b2fd7df00752396  Cargo.lock
```

## Earlier failures and corrections

The minimal Ubuntu image initially lacked CA certificates, causing Pixi's HTTP
client to panic. `PIXI_TLS_ROOT_CERTS=webpki` did not prevent that initialization
failure. Installing the normal system trust store resolves it while preserving
TLS verification. The first contributor-tool check also failed because Git was
missing. The fixture now installs Git as an explicit host prerequisite, matching
the contributor setup, instead of adding it to the project dependency lock.

The initial conclusion that Rust activation was necessary was too strong: it
had not compared plain Rust. The native-package comparison above corrected that
assumption. The final clean run validates removal of the extra activation,
direct GCC/sysroot pins, populated default mirror and custom glibc override.

## Review and limits

The development guide's build/run, formatting and Clippy commands passed.
Additional local checks passed:

```sh
pixi run --locked -e build cargo metadata --locked --offline --no-deps --format-version 1
bash -n experiments/pixi-toolchain/verify.sh
git diff --check
```

A temporary document/lock inspection helper checked local links and fragments,
newlines/whitespace, historical journal preservation, Cargo manifest/lock
consistency and package/environment isolation. It used host Python 3.14.4,
PyYAML 6.0.3 and markdown-it-py 3.0.0; it is not required contributor tooling.
Rendered documentation and historical external link availability were not
exhaustively checked.

The native compiler driver and sysroot remain transitive linker requirements;
removing direct declarations does not remove their locked packages. Git version
reproducibility is deliberately outside the project environment contract.
This proves bootstrap building on the reference userspace/current host kernel,
not bit-identical output, offline fresh installation, older kernels, all glibc
2.28 hosts, packaged deployment or robot operation. Revisit after toolchain/Pixi
upgrades, native dependency changes or a wider platform matrix. The development
guide owns supported commands and prerequisites.
