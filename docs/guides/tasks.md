# Task reference

Run tasks from the repository with `pixi run --locked TASK` for build/run and
`pixi run --locked -e dev TASK` for contributor checks. The
[manifest](../../pixi.toml) owns exact commands, dependencies and environment
routing; this page explains how to choose tasks and use them safely.
See the [development guide](development.md) for setup and upgrades.

## Commands and scopes

| Task | Purpose | Environment |
| --- | --- | --- |
| `check` | Formatting, lints and hook configuration; no test execution | `dev` |
| `format-check` | Inspect Rust formatting | `dev` |
| `lint` | Clippy on all targets (warnings fail) and hook configuration | `dev` |
| `test` | Execute all implemented workspace tests | `dev` |
| `agent-test` | Execute only the agent package tests | `dev` |
| `build` | Build all implemented components | `default` |
| `agent-run` | Build and invoke the bootstrap diagnostic | `default` |
| `format` | Rewrite source formatting | `dev` |
| `fix` | Apply available lint/compiler suggestions | `dev` |
| `clean` | Remove repository build output | `default` |

Root tasks currently cover the Rust workspace, not Markdown validation, Python
or frontend code. Add validators with their components. The `rust-*` tasks
provide focused Rust equivalents; `rust-check` excludes hook validation.
Run `check` and `test` separately for complete validation. Clippy compiles test
targets but does not execute tests.

Tasks fail nonzero on tool, environment or lock errors; aggregates propagate
failures. Checks may update caches/build output, but must leave tracked source
and locks unchanged, including on failure. Tasks do not declare output caching;
Cargo may reuse compilation output. Inspect fixes and rerun `check` afterward.

## Feature and environment composition

`default` provides build/run tools. `dev` inherits those and adds the `test`
and `lint` features. Both share tool versions through one solve group.
[ADR 0001](../adr/0001-pixi-cargo-and-task-ownership.md) owns this decision;
[Pixi's manifest reference](https://pixi.prefix.dev/latest/reference/pixi_manifest/#the-feature-and-environments-tables)
explains composition. Workload releases have independent runtime manifests/locks.

Tasks run from the workspace root, including when invoked from a component
directory. Forward CLI arguments after `--`:

```sh
pixi run --locked agent-run -- --help
pixi run --locked agent-run -- --version
```

The [README](../../README.md#current-state) describes the diagnostic; the
[development guide](development.md#build-and-inspect-the-bootstrap-package)
explains its exit behavior. Commit tasks below accept their indicated argument;
other tasks have no supported extra arguments. Use explicit tool commands for
other scopes.

## Hooks and commit messages

| Task (in `dev`) | Purpose |
| --- | --- |
| `hooks-install` | Install pre-commit and commit-msg Git shims |
| `hooks-check` | Run check-only hooks on all current working-tree files |
| `hooks-validate` | Validate `prek.toml` |
| `commit-check PATH` | Validate one UTF-8 commit-message file |
| `commit-check-range RANGE` | Validate messages in an explicit Git revision set |

Install hooks once per clone; reinstall after moving the checkout or recreating
the environment. Keep Pixi and Git on `PATH`. Existing hooks or `core.hooksPath`
may require contributor resolution; inspect prek's migration notice rather than
force-overwriting them. Installation is separate from validation.

[prek.toml](../../prek.toml) is the sole hook configuration. Local system hooks
invoke locked dev tasks without separate language environments. Pre-commit
checks the entire repository through `check`, including docs-only commits and
deletions; it does not run tests or stage/fix files. Keep `hooks-check` out of
`check` and its dependencies to avoid recursion.

At commit time, prek temporarily sets unstaged tracked edits aside to check the
staged snapshot, then restores them. Do not interrupt restoration; inspect Git
status after an interrupted run. Untracked files remain visible and can affect
workspace checks. Prek refuses unstaged hook-configuration edits. `hooks-check`
instead inspects the current working tree; passing it does not prove that a
partially staged commit passes.

```sh
pixi run --locked -e dev commit-check '/tmp/commit message.txt'
pixi run --locked -e dev commit-check-range 'origin/main..HEAD'
```

Pass the path/range directly, without an extra `--`. Missing arguments, unknown
revisions, empty ranges and invalid/empty messages fail.
[.cz.toml](../../.cz.toml) owns the Conventional Commits schema and the `Merge `
prefix exemption. Revert, fixup and squash subjects have no prefix exemption.
Syntax validation does not judge imperative wording or commit coherence; follow
the [working agreement](../working-agreement.md#review-commits-and-publication).

`BASE..HEAD` excludes the base. A single revision such as `HEAD` checks all
reachable history, including the root; choose the proposed head deliberately
when CI supplies a synthetic merge. All-file hooks neither validate messages
nor audit history. See [PR checks](development.md#pr-checks),
[prek's reference](https://prek.j178.dev/reference/cli/), and
[Commitizen check](https://commitizen-tools.github.io/commitizen/commands/check/).

## Mutation and cleanup

Inspect `git status` and the diff before `format` or `fix`. Formatting can
rewrite uncommitted Rust edits. `fix` retains Cargo's Git safeguards and refuses
dirty/staged/untracked work; resolve that work deliberately. Neither task
stages, commits, hides or reverts changes. Fixes can still need manual work.

`clean` deletes generated build output, not operational state. Keep SQLite,
release catalogs, runtime state and caches outside `target/`. The task pins
final/intermediate output to repository `target/`, refuses symlinks (including
dangling ones), and retains Cargo's `CACHEDIR.TAG` safeguard. An absent `target/`
is safe. Custom external output directories require separate deliberate cleanup.
It preserves source, locks, `.pixi/` and package caches. See
[Cargo clean](https://doc.rust-lang.org/cargo/commands/cargo-clean.html).

## Editor and Git defaults

[EditorConfig](../../.editorconfig) owns encoding, whitespace and indentation
conventions; language formatters own code layout.
[Git attributes](../../.gitattributes) normalize detected text to LF in the
index and checkout, leaving binary data unchanged.
[Git ignores](../../.gitignore) identify generated environments/build output.
Keep source, lockfiles and shared editor conventions tracked.
