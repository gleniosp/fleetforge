# Canonical task and editor validation

- **Date:** 2026-10-21
- **Delivery:** [M0-05, issue #5](https://github.com/gleniosp/fleetforge/issues/5)
- **Source:** Working tree on `build/5-canonical-pixi-tasks`, based on
  `c8fc745b0eed2ae295edd9c0ae0f37c2f95d2b44`.
- **Contract:** [Task reference](../guides/tasks.md),
  [ADR 0001](../adr/0001-pixi-cargo-and-task-ownership.md),
  [MVP-01](../product/requirements.md#mvp-01--engineering-foundation).

## Setup and implementation

Used the existing Linux x86_64 host and pinned environments. Pixi was 0.82.1,
within the required 0.82.x series. The existing lock supplies Rust/Cargo 1.98.1,
rustfmt 1.9.0-stable and Clippy 0.1.98. No package, package version, environment
feature or lockfile changed. Host Python 3.14.4 orchestrated temporary validation
helpers; it is not a new contributor prerequisite.

Consulted the current official [Pixi tasks](https://pixi.prefix.dev/latest/workspace/advanced_tasks/),
[run](https://pixi.prefix.dev/latest/reference/cli/pixi/run/),
[Clippy usage](https://doc.rust-lang.org/clippy/usage.html),
[Cargo fix](https://doc.rust-lang.org/cargo/commands/cargo-fix.html),
[Cargo clean](https://doc.rust-lang.org/cargo/commands/cargo-clean.html),
[Cargo configuration](https://doc.rust-lang.org/cargo/reference/config.html#buildbuild-dir),
[rustfmt](https://github.com/rust-lang/rustfmt),
[EditorConfig](https://editorconfig.org/) and
[Git attributes](https://git-scm.com/docs/gitattributes) documentation.

Pixi 0.82.1 rejected `default-environment` on a commandless alias. The final
configuration uses package-free aliases in `default`, dependency edges with
explicit tool environments, and `default-environment` on command tasks in the
shared Rust feature. `pixi task list --summary` and locked dry runs of `check`,
`build` and `rust-format-check` verified discovery/routing without prompts.
Root build/clean route to `build`; validation/format/fix route to `dev`.

## Task execution and failure checks

Ran these real-workspace commands, hashing all tracked and new source/config
files before and after each invocation:

```sh
for task in check lint format-check test build rust-check rust-lint rust-format-check rust-test rust-build; do
  pixi run --locked "$task"
done
```

All returned zero, including the 10 existing CLI integration tests. Every
source/config/lock hash was unchanged. `pixi run --locked format` also passed
without a Rust source diff. `pixi run --locked fix` returned 101, explicitly
refusing this delivery's uncommitted work; it did not rewrite it.

A disposable repository copied the same tracked/new files, excluding ignored
environments/build output. Initialized and committed **only that fixture** to
exercise Cargo's clean/dirty/staged safeguards, and let Pixi install its locked
environments. Sandbox access to Pixi's external cache lock failed; the authorized
rerun outside the sandbox provisioned those fixture environments successfully.
No commits or staging were performed in FleetForge's working tree.

In the clean fixture, ran the initial 16 task names with `pixi run --locked TASK`:
`check`, `lint`, `format`, `format-check`, `fix`, `test`, `build`, `clean`, and
each corresponding `rust-*` task. All passed and preserved source and locks.
Then applied each input below separately, restoring fixture bytes afterward.
Every failing non-mutating invocation preserved the injected input and locks.

| Input / exact command family | Observed result |
| --- | --- |
| Replace `fn main() -> io::Result<ExitCode> {` with `fn main()->io::Result<ExitCode>{`; run `format-check`, `rust-format-check`, `check`, `rust-check` | Nonzero; both `format` and `rust-format` separately restored the original formatted source |
| Add `let lint_failure = 1;` at the start of `main`; run `lint`, `rust-lint`, `check`, `rust-check` | Nonzero; unused-variable warning denied |
| Run `fix` and `rust-fix` with the fixture's dirty source, then staged source, then a separate untracked file | Each refused uncommitted work without rewriting it |
| Commit fixture input `let mut fixable = 1; let _ = fixable;` in `main`; run each of `fix` and `rust-fix` from a clean fixture | Both removed `mut`; subsequent `check` passed |
| Append `#[test] fn injected_failure() { panic!("task failure sentinel"); }` to `apps/agent/tests/cli.rs`; run `test`, `rust-test`, `check`, `rust-check` | Nonzero; injected test failed |
| Append `compile_error!("task build failure sentinel");` to `main.rs`; run `build`, `rust-build`, `check`, `rust-check` | Nonzero; compilation failed |
| Change workspace version from `0.1.0` to `0.1.1` without updating `Cargo.lock`; run `build`, `lint`, `test`, `check` | Nonzero; Cargo rejected the stale lock |
| Change the Pixi Rust pin from `=1.98.1` to `=1.98.0` without updating `pixi.lock`; run `check` | Nonzero; Pixi rejected the stale lock before tool execution |

## Cleanup safety

For each of `clean` and `rust-clean`, first ran `rust-build` with the default
output configuration, creating real `target/` output and Cargo's `CACHEDIR.TAG`.
Added a generated sentinel there and preservation sentinels at
`state/agent.sqlite`, `releases/catalog`, `runtime/active`, `cache/package`,
`.pixi/keep`, `external-output/keep` and `external-intermediate/keep`.
Added fixture `.cargo/config.toml`:

```toml
[build]
target-dir = "external-output"
build-dir = "external-intermediate"
```

From fixture `apps/agent`, ran both cleanup tasks separately with these
environment overrides (absolute fixture paths in the actual execution):

```sh
CARGO_TARGET_DIR="$TASK_FIXTURE/external-output" \
CARGO_BUILD_BUILD_DIR="$TASK_FIXTURE/external-intermediate" \
pixi run --locked clean
# Repeat with rust-clean after rebuilding root target/ with default output settings.
```

Both removed only root `target/`, preserved all sentinels and source/locks, and
succeeded when repeated with `target/` absent. Both refused a live symlink from
`target/` to `state/`, a dangling symlink, and an existing unmarked directory
containing an unrelated file. The preservation sentinels survived every case.

An initial cleanup fixture manually recreated `target/` after deletion; Cargo
correctly refused it because it lacked `CACHEDIR.TAG`. The corrected fixture
lets Cargo create the directory during a real build before injecting the
generated sentinel. It temporarily removes the external-output configuration
during that build, then restores it for cleanup. No marker is fabricated and no
Cargo safety check is disabled. A final `check` from fixture `apps/agent` passed.

## Editor, Git and review

Parsed EditorConfig properties: two-space defaults, four-space Rust/Python,
LF/final newline, and Markdown trailing-whitespace preservation. Compared
`git hash-object --stdin --path sample.txt` on CRLF text with a raw LF blob:
hashes matched. A NUL-containing binary with CRLF matched its raw blob unchanged.
`git check-ignore --no-index --stdin` ignored only `.pixi/example` and
`target/example` among those paths, `Cargo.lock`, `pixi.lock`, `.editorconfig`
and `apps/agent/src/main.rs`. Reviewed defaults against rustfmt indentation.

Reviewed the full change, local documentation links/heading fragments, fences,
final newlines and `git diff --check`. Both lockfiles and Rust source/tests are
unchanged from the base revision. The supported task contract is in the guide;
temporary Python helpers and disposable repositories are validation aids.

## Limits

This validates task behavior and failure propagation on the current Linux host.
The cleanup state files are sentinels, not operational FleetForge databases or
runtime fixtures. Editor properties were inspected rather than exercised in a
GUI editor; Python formatting tooling still belongs to its future owning
delivery. No fresh Ubuntu container/toolchain experiment, hook installation,
GitHub Actions execution or other-platform check was performed. Toolchain
provisioning evidence remains in the [existing experiment](../experiments/0001-pixi-toolchain.md).

## Review follow-up: agent invocation and Git attributes

At maintainer request, expanded the task reference's explanation of
`* text=auto eol=lf` and introduced `agent-run` as the seventeenth task. It uses
`cargo run --locked -p fleetforge-agent --` in `build`, keeping the executable's
argument boundary in the task itself. README and development examples now use
the shorter invocation. No package or lock change was needed.

Ran `pixi run --locked agent-run`, plus `pixi run --locked agent-run -- --help`
and `pixi run --locked agent-run -- --version`: all returned zero with the
documented CLI output. `pixi run --locked agent-run -- --not-an-option` returned
2, preserving the CLI usage-error status. Passing one argument containing
spaces also returned 2 and reported it as a single unexpected argument.
The version command passed when invoked from `apps/agent`. Hashes of all
tracked/new source, configuration and lockfiles were unchanged across these
invocations. Rechecked documentation links, fences, final newlines and diff
whitespace after updating the guides.
