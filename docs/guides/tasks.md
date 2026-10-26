# Task reference

Select non-default scopes explicitly: `pixi run --locked -e host TASK` for
contributor work and `pixi run --locked -e device TASK` for device work. Default
Rust tooling needs no environment flag. The [manifest](../../pixi.toml) owns
commands and versions; the [development guide](development.md) owns setup.

## Pixi configuration conventions

- Keep the manifest in one place. Group each feature's dependencies, tasks and
  platform overrides together; keep environment composition together at the end.
- Use exactly the implicit default, `lint` and `test` feature roles. Default
  owns build/run/clean, lint owns repository checks and setup,
  and test owns tests. Put device-prefixed aggregates and component leaves in
  their corresponding feature's Linux target table, not separate device features.
- Put tasks in their owning feature, including native target tables; never put
  tasks under environments. Environments select features/platforms only.
- Tasks and dependencies do not select environments or invoke Pixi to switch
  environments. Callers, CI and hooks explicitly select non-default environments
  with `-e`; omission is reserved for default tooling.
- Define component commands once, then compose aggregates through task names.
  Keep checks non-mutating, format/fix explicit, and tests separate. Pre-commit
  calls the repository-wide `fix` aggregate. Host `check` directly composes
  focused checks without invoking the hook runner. No hook calls `check` back.
  Do not add empty tasks for future components.

## Commands and scopes

| Task                                   | Purpose                                                             | Environment |
| -------------------------------------- | ------------------------------------------------------------------- | ----------- |
| `setup`                                | Prepare formatter plugin and install contributor hooks              | `host`      |
| `check`                                | Compose read-only host formatting/configuration checks              | `host`      |
| `fix`                                  | Apply current host fixes across the repository                      | `host`      |
| `format`, `format-check`               | Rewrite/check eligible document/configuration files; optional paths | `host`      |
| `format-setup`                         | Download and compile the pinned Wasm plugin                         | `host`      |
| `device-build`, `agent-build`          | Build device apps or just the agent                                 | `device`    |
| `device-check`, `agent-check`          | Device format-check and lint; no tests                              | `device`    |
| `device-format-check`, `device-format` | Inspect/rewrite device source formatting                            | `device`    |
| `device-lint`, `device-fix`            | Device lints and Cargo-safe fixes                                   | `device`    |
| `device-test`, `agent-test`            | Execute device tests or just agent tests                            | `device`    |
| `agent-run`                            | Invoke the bootstrap diagnostic                                     | `device`    |
| `device-clean`                         | Remove generated build output                                       | `device`    |

### Feature and environment composition

Default provides shared Rust and Linux-only device build/run/clean tasks.
`lint` adds repository tooling/checks and Linux-only device source checks;
`test` owns Linux-only device tests. Both host and device select lint/test and
inherit default; device additionally restricts platforms to linux-64. Linux host
can see device-prefixed commands, but ordinary `check` never invokes them.
Callers select `-e host` or `-e device` explicitly to state the intended scope.
All environments share a solve group; deployed runtime locks remain separate.

Host `check` composes `format-check` and `hooks-validate`; `fix` composes
`format`. Add lint checks/fixes only with actual owning components. No host
application test suite is introduced. `format`/`format-check` use one dprint
configuration over current Markdown, JSON/JSONC, YAML and TOML, including
eligible untracked files when no paths are supplied. The
[formatting guide](development.md#repository-formatting) owns exclusions,
configuration ownership and editor setup. Rust keeps its device-scoped tasks.

Tasks run from the workspace root, including when invoked from a component
directory. Forward CLI arguments after `--`:

```sh
pixi run --locked -e device agent-run -- --help
pixi run --locked -e device agent-run -- --version
```

The [README](../../README.md#current-state) describes the diagnostic; the
[development guide](development.md#build-and-inspect-the-bootstrap-package)
explains its exit behavior. Commit tasks below accept their indicated argument;
`format` and `format-check` accept optional paths. Other tasks have no supported
extra arguments. Use explicit tool commands for other scopes.

## Hooks and commit messages

| Task (in `host`)           | Purpose                                           |
| -------------------------- | ------------------------------------------------- |
| `hooks-install`            | Install pre-commit and commit-msg Git shims       |
| `hooks-validate`           | Validate `prek.toml`                              |
| `commit-check PATH`        | Validate one UTF-8 commit-message file            |
| `commit-check-range RANGE` | Validate messages in an explicit Git revision set |

Install hooks once per clone; reinstall after moving the checkout or recreating
the environment. Keep Pixi and Git on `PATH`. Existing hooks or `core.hooksPath`
may require contributor resolution; inspect prek's migration notice rather than
force-overwriting them. Installation is separate from validation.

[prek.toml](../../prek.toml) is the sole hook configuration. Pre-commit runs
three non-formatting safety built-ins and a single repository-wide `fix` hook.
Commit messages use the separate `commit-check` hook. There is no formatting
check hook: use host `check` or `format-check` directly during development.
CI runs the direct checks and invokes Prek with `--skip fix` for commit safety.

The `fix` hook runs without filename arguments, so it covers all eligible files,
including untracked drafts. Changes to tracked/staged content stop the commit:
review and restage the intended fixes before retrying. Prek never stages them
for you. Untracked fixes may not stop a commit by themselves.

At commit time, Prek temporarily sets unstaged tracked edits aside and restores
them afterwards. If restoration conflicts with fixes, it rolls those fixes back
before restoring the tracked edits. Untracked files stay visible and may be
formatted by the repository-wide hook. Do not interrupt restoration; inspect
Git status after an interrupted run. Prek refuses unstaged hook-configuration
edits. Passing a working-tree `check` does not prove a partially staged commit
passes. To run the commit hooks explicitly, use
`pixi run --locked -e host prek run --all-files --stage pre-commit`.

```sh
pixi run --locked -e host commit-check '/tmp/commit message.txt'
pixi run --locked -e host commit-check-range 'origin/main..HEAD'
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

Inspect `git status` and the diff before repository/device/agent format or fix tasks.
Repository `format` may rewrite eligible untracked files as well as tracked files.
Formatting can rewrite uncommitted Rust edits. Cargo fix retains Git safeguards and refuses
dirty/staged/untracked work; resolve that work deliberately. Neither task
stages, commits, hides or reverts changes. Fixes can still need manual work.

`device-clean` optionally removes generated Rust output from this checkout's `target/`;
the next build recompiles it. It preserves source, locks, Pixi environments,
package caches and operational data (which must stay outside `target/`). The
same guard runs on Linux, macOS and WSL2: it refuses symlinks—paths pointing
elsewhere—even when their destination is missing, and overrides Cargo's final
and intermediate output settings so cleanup stays inside the checkout. Custom
external build directories require separate cleanup. See
[Cargo clean](https://doc.rust-lang.org/cargo/commands/cargo-clean.html).

## Editor and Git defaults

[dprint.json](../../dprint.json) owns document/configuration formatting;
[EditorConfig](../../.editorconfig) covers only explicit fallback files without
a dedicated formatter. Rust and Python retain their language formatter owners.
[Git attributes](../../.gitattributes) normalize detected text to LF in the
index and checkout, leaving binary data and canonical `release.json` bytes unchanged.
[Git ignores](../../.gitignore) identify generated environments/build output.
Keep source, lockfiles and shared editor conventions tracked.
