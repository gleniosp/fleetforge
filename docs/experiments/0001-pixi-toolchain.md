# Locked Pixi Rust toolchain validation

- Validated: 2026-10-31
- Requirement: [MVP-01](../product/requirements.md#mvp-01--engineering-foundation)
- Decision: [ADR 0001](../adr/0001-pixi-cargo-and-task-ownership.md)
- Source: working tree based on `97f88ce2a7e57090ff27501abf965079382442c2`

## Question and method

Can the locked native Rust package provide compiler, formatter, linter and linker
without host compiler tools, while keeping contributor tools out of the default
environment and rejecting manifest/lock drift without rewriting source?
Stop after fresh installation, isolated tool-path checks, builds and execution,
formatting/Clippy, and the controlled lock/lint failures below.

The [container fixture](../../experiments/pixi-toolchain/README.md) uses pinned
Ubuntu and Pixi images and copies explicitly selected configuration and agent
source files. No host source, executable or cache is mounted. Its script checks
that compiler/contributor tools are absent before installation, copies regular
non-symlink inputs into a fresh workspace and runs `pixi install --locked --all`.
Each default/device environment builds into its own output directory. Host Git
and CA certificates are image prerequisites; apt repositories remain live.

The official [Rust tutorial](https://pixi.prefix.dev/latest/tutorials/rust/)
and [install reference](https://pixi.prefix.dev/latest/reference/cli/pixi/install/)
were consulted. The installed Pixi 0.83.0 flags and the actual failure cases
validate compatibility with the current locks. This rerun validates the selected
native Rust configuration; it does not compare alternative package compositions.

## Reproduce

From the repository root with Docker and Compose:

```sh
docker compose -f experiments/pixi-toolchain/compose.yaml run --build --rm verify
docker compose -f experiments/pixi-toolchain/compose.yaml down
```

The first command returns the verifier's exit status. The container removes its
temporary workspace on exit, and `--rm` removes container state. The second command
removes the Compose network. The script owns the exact checks and disposable
mutations; the [guide](../../experiments/pixi-toolchain/README.md) explains usage.

## Setup and results

The run exited zero on Linux x86_64 with Docker Engine 29.9.2 and Compose v5.6.1.
Container userspace reported Ubuntu 24.04.5 LTS, glibc 2.39, Git 2.43.0 and
CA certificates `20260816ubuntu0.24.04.1`. The Dockerfile pins image digests.

| Check                | Observed result                                                                                                                            |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Managed tools        | Pixi 0.83.0; rustc/Cargo 1.98.1; rustfmt 1.9.0-stable; Clippy 0.1.98                                                                       |
| Linker               | Conda GCC 16.2.0; Rust executables and linker resolve beneath each tested environment's `bin/`                                             |
| Environment boundary | Default has no Prek, Commitizen or dprint; device/host provide Prek 0.5.7, Commitizen 4.19.2 and dprint 0.63.0; Git remains `/usr/bin/git` |
| Positive builds      | Fresh default/device debug builds, release build, Rust formatting and Clippy with warnings denied passed                                   |
| Execution            | `fleetforge-agent 0.1.0 (x86_64-linux; bootstrap diagnostic)`                                                                              |
| Pixi lock drift      | Changing Rust to 1.98.0 makes locked install and locked run fail                                                                           |
| Cargo lock drift     | Changing workspace version to 0.1.1 makes the locked offline build fail                                                                    |
| Inherited lint       | Injecting an unsafe block fails with `usage of an unsafe block`                                                                            |
| Source preservation  | Hash snapshots match after successful checks, each expected failure and restoration                                                        |

Lockfile SHA-256 values for reproduction:

- `pixi.lock`: `d13bdf9ac240e268bcae908f5356d700cb7dd3adb23662e26f7a115823c469c9`
- `Cargo.lock`: `0bdbd3f77349171917b2f8568c86b123306747a32dd0f9ae7b2fd7df00752396`

## Conclusion and limits

The current locked toolchain builds and runs the agent without host compiler
packages in the reference container. Keep native `rust` as the direct toolchain
dependency and rely on its locked transitive linker requirements.

This does not establish bit-identical outputs, offline fresh installation, other
kernels/platforms, Docker Desktop/emulation or robot operation. Repeat when Pixi,
locks, host prerequisites or supported platforms change. The current fixture is
not a replacement for the repository's complete contributor checks and tests.
