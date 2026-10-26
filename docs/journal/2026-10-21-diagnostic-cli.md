# Bootstrap diagnostic CLI evidence — 2026-10-21

**Task:** [M0-04 / issue #4](https://github.com/gleniosp/fleetforge/issues/4)

## Scope and source

Implemented in the uncommitted working tree on
`feat/4-initial-diagnostic-rust-executable`, based on
`7ea5ceb0026740fb6c680e32164a16c92e0c1c3f`.
The [executable](../../apps/agent/src/main.rs) preserves the no-argument
version/platform diagnostic and adds `--help` and `--version`. Unsupported,
combined or repeated arguments return code 2, identify the first unexpected
argument on stderr and produce no stdout. Arguments use `args_os` so invalid
UTF-8 input is rejected without a Unicode conversion panic.

The implementation uses only the standard library, stays in one source module,
and retains inherited workspace lints. No manifests, dependencies or lockfiles
change. The [README](../../README.md) provides invocation examples; the
[development guide](../guides/development.md#build-and-inspect-the-bootstrap-package)
owns the CLI contract and validation commands.

Consulted current official documentation for
[OS-native arguments](https://doc.rust-lang.org/std/env/fn.args_os.html),
[Cargo integration tests and binary discovery](https://doc.rust-lang.org/cargo/reference/cargo-targets.html#integration-tests),
[Cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html),
[Cargo argument forwarding](https://doc.rust-lang.org/cargo/commands/cargo-run.html),
and [Pixi run](https://pixi.prefix.dev/latest/reference/cli/pixi/run/).
Checked installed Pixi's help for environment/locked options and exercised the
documented commands with the repository's pinned Rust toolchain. This is routine
implementation validation under ADR 0003; no new architectural decision or
package-manager configuration is needed.

## Setup and commands

Validation host: Ubuntu 26.04.1, Linux `7.0.0-38-generic`, x86_64.
Pixi 0.82.1 satisfies the manifest's 0.82.x constraint. Its existing named
environments supplied Rust/Cargo 1.98.1, Clippy 0.1.98 and rustfmt 1.9.0-stable.
Commands ran from the repository root:

```sh
pixi --version
pixi run --help
pixi run --locked -e dev rustc --version
pixi run --locked -e dev cargo --version
pixi run --locked -e dev cargo clippy --version
pixi run --locked -e dev cargo fmt --version
pixi run --locked -e dev cargo fmt --all
pixi run --locked -e dev cargo fmt --all -- --check
pixi run --locked -e dev cargo test --workspace --locked
pixi run --locked -e dev cargo clippy --workspace --all-targets --locked -- -D warnings
pixi run --locked -e build cargo build --workspace --locked
pixi run --locked -e build cargo run --locked -p fleetforge-agent
pixi run --locked -e build cargo run --locked -p fleetforge-agent -- --help
pixi run --locked -e build cargo run --locked -p fleetforge-agent -- --version
git diff --exit-code -- Cargo.lock pixi.lock Cargo.toml apps/agent/Cargo.toml
git diff --check
```

## Results and limits

All six [CLI integration tests](../../apps/agent/tests/cli.rs) passed, covering
15 direct subprocess invocations. Assertions check exact stdout/stderr and exit
codes for default/help/version, unsupported flags, positional arguments, an empty
argument, `--`, combined/repeated options, and a Unix non-UTF-8 argument.
The error cases return 2 with no success output; successful cases return 0 with
empty stderr. Tests locate the built executable through Cargo's
`CARGO_BIN_EXE_fleetforge-agent` variable rather than a host PATH lookup.

The initial formatting check requested a layout change; applied rustfmt and
reran the formatting check successfully. Tests passed again after formatting.
Clippy passed with warnings denied, the build environment compiled the workspace,
and all three documented invocations produced the expected output. Manifest and
lockfile comparison against HEAD passed. Reviewed the complete source/test and
documentation changes, local link destinations/fragments, fenced blocks, final
newlines and diff whitespace.

This verifies the bootstrap CLI on the current Linux host with existing Pixi
environments. A fresh Ubuntu 24.04 container installation was not repeated;
toolchain provisioning evidence remains in the
[existing experiment](../experiments/0001-pixi-toolchain.md). No operational
agent, ROS workload, CI execution or other-platform behavior is established by
these checks. Changes remain available for maintainer local review.

## Rust skill review and output-error correction — 2026-10-21

Reviewed the implementation against the maintainer's updated `rust-engineering`
skill. Ownership, the small `Action` enum, OS-native arguments, inherited lints
and dependency-free subprocess tests fit the present scope. The concrete gap was
ordinary output errors: the original `println!`/`eprintln!` calls panicked on
a closed stdout pipe or Linux `/dev/full`, returning 101. Both stdout failure
cases were reproduced with captured panic output; failing stderr also returned 101. This is a routine error-path correction within #4.

Changed `main` and the invalid-argument helper to return `io::Result<ExitCode>`.
Fallible writes to locked streams and explicit flushes propagate errors through
`?`. Rust's standard `Result` termination reports an I/O error when stderr works
and returns failure even when reporting also fails. Normal success remains 0;
reported invalid input remains 2; output failure returns 1. The
[development guide](../guides/development.md#build-and-inspect-the-bootstrap-package)
now documents that distinction. No additional error framework or dependency was
introduced.

Consulted official documentation for
[Result termination](https://doc.rust-lang.org/std/process/trait.Termination.html),
[fallible writes and flushing](https://doc.rust-lang.org/std/io/trait.Write.html),
and [anonymous pipes](https://doc.rust-lang.org/std/io/fn.pipe.html).
`std::io::pipe` is stable since Rust 1.87, compatible with the pinned 1.98.1.
The pipe test closes the reader before spawning the executable, avoiding a
consumer-timing race. Linux device tests open `/dev/full` without creating or
changing a filesystem file.

Ran focused regression tests, then the relevant gates:

```sh
pixi run --locked -e dev cargo fmt --all
pixi run --locked -e dev cargo test --locked -p fleetforge-agent --test cli io_failure
pixi run --locked -e dev cargo fmt --all -- --check
pixi run --locked -e dev cargo check --workspace --all-targets --locked
pixi run --locked -e dev cargo clippy --workspace --all-targets --locked -- -D warnings
pixi run --locked -e dev cargo test --workspace --locked
pixi run --locked -e dev cargo test --workspace --locked --release
pixi run --locked -e build cargo build --workspace --locked
git diff --exit-code -- Cargo.lock pixi.lock Cargo.toml apps/agent/Cargo.toml
git diff --check
```

All four new regression tests passed; all ten integration tests then passed in
both debug and release profiles (23 subprocess invocations per full run).
They cover each successful action with a closed stdout pipe and full output
device, failure to write an invalid-argument diagnostic, and simultaneous
stdout/stderr failure. Captured I/O diagnostics begin with `Error:` and contain
no panic output; tests avoid coupling to OS error wording. A failed stderr
cannot be captured, so those cases assert the controlled exit code 1 and empty
stdout where captured. Formatting, checking, Clippy, build and manifest/lock
comparison passed. Local documentation links/fragments and whitespace were
reviewed again. Platform limits remain as recorded above; device tests are
Linux-only and the closed-pipe test is Unix-only.
