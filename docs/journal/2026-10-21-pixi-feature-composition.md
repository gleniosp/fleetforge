# Default, test and lint feature composition

- **Date:** 2026-10-21
- **Delivery:** [M0-05, issue #5](https://github.com/gleniosp/fleetforge/issues/5)
- **Source:** Working tree on `build/5-canonical-pixi-tasks`, based on
  `7a5d47d9130d27f6ab50f138d5220b1835c4b67d`.
- **Contract:** [MVP-01](../product/requirements.md#mvp-01--engineering-foundation),
  [ADR 0001](../adr/0001-pixi-cargo-and-task-ownership.md) and
  [task composition](../guides/tasks.md#feature-and-environment-composition).

## Direction and implementation

The maintainer requested a default feature containing essential build/run
dependencies and tasks, separate test/lint capability features, and one named
dev environment that inherits default and composes both. This revises the
earlier separate dev/build environment decision within #5, before publication.
Updated that issue's scope and acceptance criteria, plus the owning requirement,
ADR, guides, manifest, lock and reference-container fixture. Earlier observations
remain in the [initial task journal](2026-10-21-canonical-tasks.md) and
[toolchain experiment](../experiments/0001-pixi-toolchain.md).

The default feature now supplies Rust, build/run and cleanup tasks. Test owns
the two test tasks without additional packages, because Cargo supplies Rust
test support. Lint owns lint/format/fix tasks, prek and Commitizen. Rustfmt and
Clippy are already bundled with Rust. Dev composes both checking features and
inherits default; its environment-local `check` and `rust-check` tasks combine
their checks. Default and dev share the `toolchain` solve group. No other named
environment or language feature is introduced.

Consulted the current official [manifest reference](https://pixi.prefix.dev/latest/reference/pixi_manifest/),
[task documentation](https://pixi.prefix.dev/latest/workspace/advanced_tasks/)
and [environment guide](https://pixi.prefix.dev/latest/workspace/multi_environment/).
The installed Pixi 0.82.1 parsed environment-local aggregates, default-feature
inheritance and shared solve-group membership. It rejected the stale lock
before an intentional `pixi lock`. This required access to Pixi's external
metadata cache, which the sandbox initially blocked; the authorized rerun
succeeded. The subsequent locked installation also needed that cache access.

## Lock and routing checks

Compared parsed locks against `git show HEAD:pixi.lock`: the entire package
record list and dev environment entry are identical. The new default entry is
identical to the former build entry. There are 17 default and 54 dev packages.
Only the environment membership changes; versions, artifact URLs and hashes do
not change. Cargo.lock is byte-for-byte unchanged.

```sh
pixi lock
pixi install --locked --all
pixi task list --summary
pixi run --locked --dry-run build
pixi run --locked --dry-run -e dev check
pixi run --locked --dry-run check
pixi run --locked --dry-run -e dev build
```

Dry runs showed builds in default, checks in dev, and inherited build aliases
routing to default without a selection prompt. Task-list JSON confirms exactly
five default tasks; dev inherits those and adds the two test tasks, eight lint
tasks and two environment-local aggregates. All 17 task names retain their
implemented behavior. Prek/Commitizen and the Python contributor stack remain
outside default; no new direct or transitive package is added.

## Fresh reference-container validation

Used the existing prerequisite-only image
`fleetforge-toolchain-evidence:issue-3`, ID
`sha256:412c5015000933c71ddd41fe03cd91cdcc053f6781a9923ebdf9b97bae7d46cd`.
Its Dockerfile pins Ubuntu 24.04 and supplies host Git and CA certificates.
The fresh container had Ubuntu 24.04.5 userspace, glibc 2.39 and Git 2.43.0.
Mounted source and the Pixi executable read-only, with no host Cargo home,
environment or package cache mounted. Pixi 0.82.1's SHA-256 was
`37dc14ed94ed45dafd89f3bb3db95d42fb2063d303c5523a7652b5d93449e9b2`.

```sh
docker run --rm --name fleetforge-issue5-default-dev \
  --mount type=bind,src="$PWD",dst=/source,readonly \
  --mount type=bind,src="$(command -v pixi)",dst=/usr/local/bin/pixi,readonly \
  fleetforge-toolchain-evidence:issue-3 \
  bash /source/experiments/pixi-toolchain/verify.sh
```

The updated fixture returned zero and:

```text
PASS: fresh installs, isolated tool paths, builds, lock rejection, inherited unsafe lint, source preservation
```

It freshly installed default/dev, verified compiler/Cargo/formatter/Clippy and
linker paths under each environment, and confirmed default has no prek, cz or
Python. Both environments compiled/linked with separate output trees; the
release build and exact bootstrap diagnostic passed. Rust/Cargo remained
1.98.1, rustfmt 1.9.0-stable and Clippy 0.1.98. Deliberate stale Pixi/Cargo locks
and an unsafe-code injection were rejected without rewriting source or locks;
restoring inputs recovered the original hashes.

## Task and failure validation

Validated the routed task interface in a disposable Git copy with the updated
locked environments. The baseline fixture contains the exact working-tree
source/configuration and a fixture-only initial commit for Cargo's Git safety
checks. No staging or commit operation was performed in FleetForge's working
tree. Temporary host Python 3.14.4 helpers orchestrated these checks; they are
not supported contributor dependencies.

Ran the following task groups with source/config/lock hashes checked before
and after every non-mutating call. Format/fix were also exercised on a clean
fixture and left its already-correct source unchanged.

```sh
pixi run --locked build
pixi run --locked rust-build
pixi run --locked agent-run
for task in check rust-check test rust-test lint rust-lint format rust-format format-check rust-format-check fix rust-fix; do
  pixi run --locked -e dev "$task"
done
pixi run --locked check
pixi run --locked -e dev build
pixi run --locked -e dev agent-run -- --version
pixi run --locked agent-run -- --help
pixi run --locked agent-run -- --version
```

All returned zero, including the 10 existing CLI integration tests. Unqualified
`check` selected dev automatically; `-e dev build` delegated to default.
`agent-run -- --not-an-option` and `agent-run -- 'argument with spaces'`
returned 2. The latter reported one unexpected argument containing spaces.
Invocation from `apps/agent` also worked. Each deliberate failure below
preserved the injected source and both locks.

| Disposable input                                                                          | Commands / observed result                                                                                      |
| ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Remove spaces in `fn main() -> io::Result<ExitCode> {`                                    | Dev `format-check`, `rust-format-check`, `check`, `rust-check` failed; dev `format` restored the original bytes |
| Add unused `let lint_failure = 1;` in `main`                                              | Dev `lint`, `rust-lint`, `check`, `rust-check` failed; dev `fix`/`rust-fix` refused the dirty fixture           |
| Append formatted `#[test] fn injected_failure()` that panics with `task failure sentinel` | Dev `test`, `rust-test`, `check`, `rust-check` failed with the injected test                                    |
| Change workspace version from `0.1.0` to `0.1.1` without a Cargo lock update              | Default `build`/`agent-run` and dev `check` rejected the stale lock                                             |
| Change Rust pin from `=1.98.1` to `=1.98.0` without a Pixi lock update                    | Default `build` and dev `check` rejected the stale lock                                                         |

For each of `pixi run --locked clean` and `rust-clean`, built real root
`target/` output first, verified Cargo's marker, then supplied external
`CARGO_TARGET_DIR` and `CARGO_BUILD_BUILD_DIR` pointing to a cache sentinel
directory. Both removed only root build output, preserved separate state/cache
sentinels, and succeeded when repeated with target absent. Both rejected live
and dangling target symlinks. A final dev `check` from `apps/agent` passed.

The live workspace also passed `pixi run --locked -e dev check`,
`pixi run --locked build` and `pixi run --locked agent-run -- --version`.
All tracked/new source, configuration and lock hashes matched before/after.
The earlier broader fix/cleanup cases remain in the initial task journal;
their underlying commands and guard flags are unchanged.

## Review and limits

Historical reports retain their original commands/results; short follow-up
notes point to this revision. The current fixture and setup/task contracts use
default/dev. Issues #6 and #7 already describe dev contributor tools and
canonical CI tasks without requiring the removed build environment; their
scope and native dependencies remain applicable.

Reviewed the full working-tree diff against the initial #5 commit and checked
local document destinations/fragments, final newlines, fenced blocks, shell
syntax and `git diff --check`. The only package-lock diff moves the former
build entry to default and removes the empty default entry. Rust source/tests,
Cargo metadata and Cargo.lock are unchanged.

This verifies root toolchain composition on Linux x86_64 and the reference
Ubuntu userspace. It does not establish packaged agent deployment, ROS runtime
behavior, other platforms, hook installation or GitHub Actions execution. The
root Rust package still includes bundled check tools in default; separating
feature ownership does not split that package. Operational cleanup checks use
sentinel files rather than a running fleet.
