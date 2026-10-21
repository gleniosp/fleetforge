# Task reference

The root [Pixi manifest](../../pixi.toml) is the task entry point, under
[ADR 0001](../adr/0001-pixi-cargo-and-task-ownership.md). Run tasks with
`pixi run --locked TASK`, without `-e`; for example:

```sh
pixi run --locked check
pixi run --locked build
pixi run --locked rust-lint
```

All tasks below were introduced in **M0, issue #5**. Root tasks cover every
implemented component, currently the Rust workspace at `apps/agent`. They do
not claim to check documentation, Python, frontend code, hooks or CI. Add those
checks with their owning deliveries. `check` and `rust-check` aggregate real
formatting, lint and test checks; Clippy and tests also compile the code.
`build` remains a separately available build in its smaller environment.

## Commands and scopes

Each root task family delegates to the corresponding `rust-*` task.
`agent-run` targets the executable directly. The commands run from the workspace
root and use the pinned Pixi-provided Cargo/toolchain.

| Task names | Underlying command or dependencies | Scope and result | Environment | Mutation |
| --- | --- | --- | --- | --- |
| `check` / `rust-check` | `rust-format-check`, `rust-lint`, `rust-test` | Aggregate workspace validation | `dev` dependencies | Generated output only |
| `lint` / `rust-lint` | `cargo clippy --workspace --all-targets --locked -- -D warnings` | Compiler and Clippy lints for all workspace targets; warnings fail | `dev` | Generated output only |
| `format` / `rust-format` | `cargo fmt --all` | rustfmt for all workspace Rust source | `dev` | Rewrites source |
| `format-check` / `rust-format-check` | `cargo fmt --all -- --check` | rustfmt inspection of all workspace Rust source; differences fail | `dev` | No source changes |
| `fix` / `rust-fix` | `cargo clippy --fix --workspace --all-targets --locked -- -D warnings` | Apply available compiler/Clippy suggestions to all workspace targets | `dev` | Rewrites source; may create build output |
| `test` / `rust-test` | `cargo test --workspace --locked` | Workspace unit, integration and documentation tests | `dev` | Generated output only |
| `build` / `rust-build` | `cargo build --workspace --locked` | Workspace default-profile compilation and linking | `build` | Generated output only |
| `agent-run` | `cargo run --locked -p fleetforge-agent --` | Build as needed, then invoke the bootstrap CLI with forwarded arguments | `build` | Generated output only; the current CLI prints and exits |
| `clean` / `rust-clean` | Host `sh`, then `cargo --config 'build.build-dir="target"' clean --locked --target-dir target` | Remove only repository `target/`; reject a symlink at that path | `build` | Deletes generated build output |

Tasks return zero on success and nonzero on tool, task, environment or lock
failure. Aggregate tasks propagate dependency failures. A formatter difference,
lint warning, failing test or compilation error therefore fails `check`.
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

## Environment routing

Root aliases and the `rust-check` aggregate live in Pixi's implicit `default`
environment. It has no packages and runs no tool commands; every dependency
that executes tools explicitly selects `dev` or `build`. The component
commands live in the shared Rust feature and set `default-environment` for
direct calls such as `pixi run --locked rust-build`. This avoids an environment
selection prompt and keeps root build/clean independent of contributor tools.

Use canonical tasks without an environment override. `dev` and `build` exclude
the default feature, so root aliases and `rust-check` are unavailable with
`-e dev` or `-e build`. For arbitrary tool commands, continue to choose the
environment explicitly, for example `pixi run --locked -e build cargo run
--locked -p fleetforge-agent`. Pixi's task working directory is the workspace
root even when invoked from a component directory. `agent-run` accepts
executable arguments after `--`:

```sh
pixi run --locked agent-run
pixi run --locked agent-run -- --help
pixi run --locked agent-run -- --version
```

The task's built-in Cargo `--` ensures these arguments reach the executable.
The outer `--` separates them from Pixi options. This is the current bootstrap
diagnostic, which prints and exits. CLI usage errors return 2; I/O errors return
1, as documented in the [development guide](development.md). Other tasks
accept no supported extra arguments; use an explicit tool command for other
scopes.

The [official Pixi task documentation](https://pixi.prefix.dev/latest/workspace/advanced_tasks/)
describes aliases, dependency environments, working directories and command
defaults; [run](https://pixi.prefix.dev/latest/reference/cli/pixi/run/)
documents the outer lock check. This configuration is validated with Pixi
0.82.1, within the project's required 0.82.x series. In that version, aliases
without a command cannot set `default-environment`; their tool-bearing
dependencies select it instead.

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
