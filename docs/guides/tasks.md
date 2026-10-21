# Task reference

The root [Pixi manifest](../../pixi.toml) is the task entry point, under
[ADR 0001](../adr/0001-pixi-cargo-and-task-ownership.md). Run tasks with
`pixi run --locked TASK` for build/run, and `pixi run --locked -e dev TASK`
for development checks; for example:

```sh
pixi run --locked -e dev check
pixi run --locked build
pixi run --locked -e dev rust-lint
```

The initial component tasks were introduced in **M0, issue #5**. Hook/commit
validation, `agent-test` and the separation of checks from test execution were
introduced in **M0, issue #6**. Root tasks cover every
implemented component, currently the Rust workspace at `apps/agent`. They do
not claim to check documentation, Python, frontend code or CI. Add validators
with their owning component deliveries.

## Commands and scopes

Each component task family delegates to the corresponding `rust-*` task.
`agent-run` targets the executable directly. The commands run from the workspace
root and use the pinned Pixi-provided Cargo/toolchain.

| Task names | Underlying command or dependencies | Scope and result | Environment | Mutation |
| --- | --- | --- | --- | --- |
| `check` | `format-check`, `lint` | Repository formatting, lint and configuration validation; no test execution | `dev` | Generated output only |
| `rust-check` | `rust-format-check`, `rust-lint` | Rust workspace formatting and lints; no test execution | `dev` | Generated output only |
| `lint` / `rust-lint` | `cargo clippy --workspace --all-targets --locked -- -D warnings`; root `lint` also runs `hooks-validate` | Compiler and Clippy lints for all workspace targets; warnings fail | `dev` | Generated output only |
| `format` / `rust-format` | `cargo fmt --all` | rustfmt for all workspace Rust source | `dev` | Rewrites source |
| `format-check` / `rust-format-check` | `cargo fmt --all -- --check` | rustfmt inspection of all workspace Rust source; differences fail | `dev` | No source changes |
| `fix` / `rust-fix` | `cargo clippy --fix --workspace --all-targets --locked -- -D warnings` | Apply available compiler/Clippy suggestions to all workspace targets | `dev` | Rewrites source; may create build output |
| `test` / `rust-test` | `cargo test --workspace --locked` | Workspace unit, integration and documentation tests | `dev` | Generated output only |
| `agent-test` | `cargo test --locked -p fleetforge-agent` | Agent package unit, integration and documentation tests | `dev` | Generated output only |
| `build` / `rust-build` | `cargo build --workspace --locked` | Workspace default-profile compilation and linking | `default` | Generated output only |
| `agent-run` | `cargo run --locked -p fleetforge-agent --` | Build as needed, then invoke the bootstrap CLI with forwarded arguments | `default` | Generated output only; the current CLI prints and exits |
| `clean` / `rust-clean` | Host `sh`, then `cargo --config 'build.build-dir="target"' clean --locked --target-dir target` | Remove only repository `target/`; reject a symlink at that path | `default` | Deletes generated build output |

Tasks return zero on success and nonzero on tool, task, environment or lock
failure. Aggregate tasks propagate dependency failures. A formatter difference,
lint warning or lint-compilation error therefore fails `check`. A test failure
fails `test`, `rust-test` and the owning package's focused test task.
Fixes may leave diagnostics requiring manual work; inspect their diff and rerun
`check` after either mutating task. Tasks do not declare Pixi output caching, so
each invocation runs validation even when Cargo can reuse compilation output.

All commands that resolve Rust dependencies use Cargo's `--locked`. `cargo fmt`
does not resolve packages, and has no `--locked` option. The outer
`pixi run --locked` independently rejects stale Pixi locks. Lockfiles and
tracked source must remain byte-for-byte unchanged during non-mutating checks,
including unsuccessful checks. Environment installation, Cargo caches and
ignored build output can change. See the [development guide](development.md)
for installation, host prerequisites and deliberate lock upgrades.

## Feature and environment composition

| Owner | Dependencies | Tasks |
| --- | --- | --- |
| Default feature | Native Rust toolchain and its transitive linker requirements | `build`, `rust-build`, `agent-run`, `clean`, `rust-clean` |
| `test` feature | None beyond inherited Cargo test support | `test`, `rust-test`, `agent-test` |
| `lint` feature | prek and Commitizen; rustfmt/Clippy are already bundled with Rust | `check`, `lint`, `format`, `format-check`, `fix`, their `rust-*` counterparts, and hook/commit validation tasks |
| `dev` environment | Inherits default and composes `test` plus `lint` | Exposes the tasks owned by those features |

The default feature provides essential build/run tools and tasks to the normal
default environment. Dev inherits those and adds the test/lint features. Both
use the `toolchain` solve group; declaring default explicitly only assigns its
group. Default excludes prek/Commitizen and their transitive contributor
packages. Rust's bundled test, formatter and lint tools do not require separate
direct dependencies. The root workspace supplies build/run tooling; workload
releases retain their separate runtime manifests and locks.

Use `pixi run --locked build` and `pixi run --locked agent-run` for application
work. Use `pixi run --locked -e dev check`, `test`, `lint` or `format-check` for
validation. Build/run/clean are inherited by dev too; their component commands
default to the default environment, and build/clean aliases explicitly route
their dependency there. Dev-only task names can also be called without `-e`:
Pixi selects their sole owning environment. No extra named test, lint, build or
language environment is required. Task ownership follows the feature that
provides the capability; component prefixes identify the code scope.

`check` depends on root `format-check` and `lint`, so added component validators
extend those roots. `test` currently delegates to `rust-test`, which executes
the entire Cargo workspace once. Use `agent-test` for the current agent app
alone. Add focused test tasks with each new app/service and include every
implemented suite in the relevant test aggregate; do not add placeholder tasks
for planned services. Run `check` and `test` separately for complete validation.

Pixi tasks run from the workspace root even when invoked from a component
directory. `agent-run` accepts executable arguments after `--`:

```sh
pixi run --locked agent-run
pixi run --locked agent-run -- --help
pixi run --locked agent-run -- --version
```

The task's built-in Cargo `--` ensures these arguments reach the executable.
The outer `--` separates them from Pixi options. This is the current bootstrap
diagnostic, which prints and exits. CLI usage errors return 2; I/O errors return
1, as documented in the [development guide](development.md). The commit tasks
below accept a message file or revision range. Other tasks accept no supported
extra arguments; use an explicit tool command for other scopes.

The [official Pixi task documentation](https://pixi.prefix.dev/latest/workspace/advanced_tasks/)
describes aliases, dependency environments, working directories and command
defaults; the [manifest reference](https://pixi.prefix.dev/latest/reference/pixi_manifest/#the-feature-and-environments-tables)
describes feature ownership, default-feature inheritance and solve groups.
[Run](https://pixi.prefix.dev/latest/reference/cli/pixi/run/) documents
the outer lock check. This configuration is validated with Pixi 0.82.1, within
the project's required 0.82.x series. Commandless aliases inherit their calling
environment unless a dependency explicitly selects another environment.

## Hooks and commit messages

These **M0, issue #6** tasks run in `dev`:

| Task | Underlying command | Scope and result | Mutation |
| --- | --- | --- | --- |
| `hooks-install` | `prek install` | Install both stages declared in `prek.toml` | Writes local Git hook shims, not source or index |
| `hooks-check` | `prek run --all-files --stage pre-commit` | Run repository-wide `check`; no test execution | Generated output/cache only |
| `hooks-validate` | `prek validate-config prek.toml` | Reject invalid hook configuration | Cache/log only |
| `commit-check PATH` | `cz check --commit-msg-file PATH` | Validate one UTF-8 message file, including Git's commit-msg input | Reads the message; no source/index changes |
| `commit-check-range RANGE` | `cz check --rev-range RANGE` | Validate messages in an explicit Git revision set | Reads history; no source/index changes |

Run `pixi run --locked -e dev hooks-install` once per clone to install
`pre-commit` and `commit-msg`. Pixi and host Git must be available when Git
invokes the shims. Prek records its installed executable path; rerun installation
after moving the checkout or recreating the environment. Installation does not
force-overwrite existing hooks; inspect prek's migration notice if other hooks
already exist. A configured `core.hooksPath` may need explicit contributor
resolution. Hook installation is separate from `check`.

`prek.toml` is the sole hook configuration. All hooks are local `system` hooks:
their entries explicitly invoke locked Pixi tasks in `dev`, so prek creates no
separate language environments and does not install host Cargo or Commitizen.
The pre-commit stage invokes repository-wide `check`, inheriting its current
and future component validators. The hook sets
`pass_filenames = false` and `always_run = true`: selected/staged paths are not
task arguments, and every commit checks the whole repository, including
deletions and commits containing only documentation. Use `format` or `fix`
deliberately after inspecting failures.

Pre-commit does not run tests or a separate build. Clippy's `--all-targets`
still compiles and lints test code; it does not execute tests and can take time
on a cold cache. Run `test` explicitly for all tests or `agent-test` for the
agent alone.

At commit time, prek checks the staged snapshot: it reports and temporarily
sets unstaged tracked edits aside, then restores them. This is prek's native
index-validation behavior, not a project stash command. Do not interrupt that
restoration; inspect Git status if a run is interrupted. Untracked files remain
visible and may influence whole-workspace checks. Prek refuses unstaged hook
configuration changes; stage the intended configuration before committing.
The all-files task instead checks current working-tree contents without setting
unstaged edits aside. Neither mode stages changes or fixes source. A passing
working-tree check therefore does not prove a partially staged commit passes.

The commit-msg hook receives exactly Git's message-file path and forwards it
to `commit-check`. Quote paths containing spaces, for example:

```sh
pixi run --locked -e dev commit-check '/tmp/commit message.txt'
pixi run --locked -e dev commit-check-range 'origin/main..HEAD'
```

Supply the argument directly after the task name; no additional `--` is needed.
Missing arguments, unknown revisions, invalid messages and empty ranges return
nonzero. `.cz.toml` selects Commitizen's Conventional Commits schema and permits
the `Merge ` prefix for Git-generated merge subjects. Revert, fixup and squash
messages have no prefix exemption. Empty messages fail. Syntax validation does
not assess whether a subject is imperative or a commit is coherent; reviewers
own those checks under the [working agreement](../working-agreement.md#review-commits-and-publication).

All-file hooks do not supply a commit message or audit history. CI's owning
delivery (#7) runs hooks, tests, builds and `commit-check-range` separately,
avoiding a duplicate `check` invocation. Range validation needs the actual base,
proposed head and sufficient history. `BASE..HEAD` excludes the base; a single
revision such as `HEAD` checks
all reachable history, including a root commit when no parent exists. Git merge
subjects pass the documented prefix exemption, while messages from both parent
histories in the selected revision set are still checked. Select the proposed
head deliberately when CI provides a synthetic merge commit.

There is no task recursion: prek calls `check`, which calls `format-check` and
`lint`. Configuration validation under `lint` invokes only
`prek validate-config`, not the hook runner. Keep `hooks-check` out of `check`
and its dependencies. See the official
[prek configuration](https://prek.j178.dev/reference/configuration/),
[prek CLI](https://prek.j178.dev/reference/cli/) and
[Commitizen check](https://commitizen-tools.github.io/commitizen/commands/check/)
references and the [hook delivery journal](../journal/2026-10-21-hooks-and-commits.md)
for validation evidence.

## Mutation and cleanup

`format` is an explicit edit command: rustfmt can rewrite existing uncommitted
Rust edits. Inspect `git status` and `git diff` first, use it only on work you
intend to format, and review the diff afterward. It does not stage, commit,
stash or revert files. `fix` retains Cargo's native Git safeguards: no
`--allow-dirty`, `--allow-staged` or `--allow-no-vcs` is supplied. It refuses
uncommitted changes, including staged or untracked files. Resolve that work's
disposition deliberately before using it; the task never hides it or bypasses
the guard. [Clippy usage](https://doc.rust-lang.org/clippy/usage.html) and
[Cargo fix](https://doc.rust-lang.org/cargo/commands/cargo-fix.html) describe the
underlying fix behavior and safeguards.

`clean` is generated-build cleanup, never an operational reset. Keep SQLite,
release catalogs, runtime state and package caches outside `target/`. The task
preserves those paths, `.pixi/`, the Cargo package cache, tracked source and
both locks. It pins both Cargo's final and intermediate output directories to
the repository `target/`, overriding user output-directory settings, and
refuses even a dangling symlink at `target/`. No Git clean/reset command or
recursive workspace deletion is involved. Outputs built in a custom external
directory require deliberate separate cleanup. Cargo also refuses an existing
directory without its valid `CACHEDIR.TAG` marker; retain that safeguard rather
than marking unrelated content as build output. Cleaning an absent `target/`
succeeds. See
[Cargo clean](https://doc.rust-lang.org/cargo/commands/cargo-clean.html) and
[output directory configuration](https://doc.rust-lang.org/cargo/reference/config.html#buildbuild-dir).

## Editor and Git defaults

[EditorConfig](../../.editorconfig) sets UTF-8, LF, a final newline, spaces and
two-space indentation by default. Rust and Python use four spaces. Markdown
keeps trailing whitespace so intentional hard line breaks survive editing;
other files trim it. Language formatters own code layout; these defaults agree
with rustfmt indentation and the planned Python formatter defaults.

[Git attributes](../../.gitattributes) contain `* text=auto eol=lf`:

- `*` matches paths throughout the repository.
- `text=auto` lets Git detect text and normalize its line endings to LF in the
  index when adding content. Detected binary content is left unchanged.
- `eol=lf` checks text out with LF rather than CRLF, regardless of a
  contributor's usual `core.autocrlf` checkout preference.

LF is a single line-feed byte (`\n`); CRLF is carriage return plus line feed
(`\r\n`). Consistent LF avoids line-ending-only diffs and CRLF problems in
Linux shell scripts. EditorConfig helps editors save files consistently;
attributes apply at Git's add/checkout boundary, including files produced by
other tools. The rule does not trim whitespace, set indentation, enforce UTF-8
or add final newlines. Markdown hard line breaks remain intact. It is a shared
repository convention rather than a prerequisite for compiling on Linux.
See Git's [text and eol reference](https://git-scm.com/docs/gitattributes#_text).

[Git ignores](../../.gitignore) cover only the
generated root `.pixi/` and `target/` directories. Source, Pixi/Cargo locks and
editor conventions remain visible to Git. No formatter for other languages or
editor-specific workspace configuration is introduced here.
