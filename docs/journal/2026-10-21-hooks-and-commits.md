# Local hooks and commit validation

- **Date:** 2026-10-21
- **Delivery:** [M0-06, issue #6](https://github.com/gleniosp/fleetforge/issues/6)
- **Source:** Working tree on `build/6-pixi-hooks-commitizen`, based on
  `83eb8d934afa4c77ad2a4b3b786423618263333e`.
- **Contracts:** [Task reference](../guides/tasks.md#hooks-and-commit-messages),
  [ADR 0001](../adr/0001-pixi-cargo-and-task-ownership.md),
  [MVP-01](../product/requirements.md#mvp-01--engineering-foundation).

## Setup and review decisions

Used Linux x86_64 (kernel 7.0.0-38-generic), Git 2.53.0, Pixi 0.82.1,
prek 0.5.6, Commitizen 4.19.2 and Rust/Cargo 1.98.1. Python 3.14.4 orchestrated
checks in temporary scripts; it is not a contributor prerequisite. Prek and
Commitizen were already locked direct dependencies in the lint feature, with
Python transitive through Commitizen. No package, pin or lockfile changed.

Consulted current official [Pixi tasks](https://pixi.prefix.dev/latest/workspace/advanced_tasks/),
[Pixi manifest](https://pixi.prefix.dev/latest/reference/pixi_manifest/),
[prek configuration](https://prek.j178.dev/reference/configuration/),
[prek CLI](https://prek.j178.dev/reference/cli/),
[Commitizen check](https://commitizen-tools.github.io/commitizen/commands/check/)
and [Cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html)
documentation. Compared installed CLI help and inspected Commitizen's `Check`
and Git-log implementation for prefix handling and revision-set semantics.

Review clarified the final boundary: prek uses root `check`, which aggregates
formatting, lint and configuration validation; tests have separate all-suite
and focused app/service tasks. Initial validation used component hooks and a
check aggregate that included tests. Those arrangements were replaced and the
final split was validated below. Check tasks now belong to the lint feature;
`agent-test` was added to the test feature. Both environments are declared
inline under `[environments]`; parsing confirms the same environment values.

The documentation review consolidated commit-writing rules in the working
agreement, setup recipes in the development guide and command/staging semantics
in the task reference. This new journal consolidates the observations from
successive review passes. Existing historical journals remain unchanged.

## Disposable Git fixture

Copied tracked and new non-ignored files from
`git ls-files --cached --others --exclude-standard -z` into a temporary directory.
Initialized it with `git init -b main`, set fixture-only name/email, disabled
commit signing and committed the baseline before installing hooks. Set
`GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null` and `PREK_HOME` under the
fixture's ignored `.pixi/`. Then ran:

```sh
pixi install --locked -e dev
pixi run --locked -e dev hooks-validate
pixi run --locked -e dev hooks-install
pixi run --locked -e dev hooks-check
```

All returned zero. Both installed hook shims were executable and referenced
Pixi's prek. `hooks-check` also passed from `apps/agent`. An initial sandbox
run could not write prek's normal external log; an approved rerun passed.
A helper invocation with unavailable host `python` was corrected to `python3`.
Fixture installation reused the existing package cache.

Prepended executable host stubs for `cargo`, `rustfmt`, `clippy-driver`, `cz`
and `prek`, each printing `host-tool-sentinel` and exiting 99. Both
`hooks-check` and `git commit -m 'test: exercise installed hooks'` passed without
that sentinel. The installed shim and nested Pixi calls resolved dev's tools.
No staging, commits or hook installation occurred in the source repository.

## Source checks and staged content

Restored valid fixture source/configuration between independent injections.
These initial staged-content checks exercised the same underlying format/lint
commands; final aggregate routing was checked separately below.

| Fixture input / command                                                                                                                               | Result                                                                         |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Valid documentation-only commit                                                                                                                       | 0; source and commit-message hooks execute                                     |
| `git commit -m 'incorrect subject'` with a staged sentinel                                                                                            | 1; message rejected, HEAD unchanged                                            |
| Stage `fn main()->io::Result<ExitCode>{` in place of the formatted `main` signature, then leave the formatted correction unstaged; try a valid commit | 1; staged format error rejected, unstaged correction restored, index unchanged |
| Stage formatted source, leave that formatting error unstaged; try a valid commit                                                                      | 0; staged source passes, unstaged error restored                               |
| Run `hooks-check` on that unstaged format error                                                                                                       | 1; current-tree check sees it, source unchanged                                |
| Add `let unused_hook_sentinel = 1;` inside `main`; run `hooks-check`                                                                                  | 1; Clippy rejects the warning                                                  |
| Add untracked `apps/agent/tests/hook_untracked.rs` containing `compile_error!("untracked hook sentinel");`; run `hooks-check`                         | 1; workspace compilation sees untracked input                                  |
| Append an unstaged comment to `prek.toml`, stage only another file, then try a valid commit                                                           | 1; prek refuses unstaged hook configuration and preserves it                   |
| Replace `prek.toml` with `this is not valid TOML`; run `hooks-validate` and `check`                                                                   | 1 for both; configuration failure propagates                                   |
| Stage only deletion of the sentinel; try a valid commit                                                                                               | 0; source checks still run                                                     |

Prek logged restoration after both successful and failed staged checks. Failed
checks preserved injected source bytes. After restoring valid inputs,
`hooks-check` passed and both locks matched the source repository.

## Final check/test split and aggregate propagation

Copied and staged the reviewed manifest/configuration in the fixture and
committed through its installed shims. Appended this formatted test to the
agent's `main.rs`:

```rust
#[test]
fn check_test_split_sentinel() {
    panic!("check test split sentinel");
}
```

| Command with the injected test                                                      | Result                                           |
| ----------------------------------------------------------------------------------- | ------------------------------------------------ |
| `pixi run --locked -e dev check`                                                    | 0; no test execution                             |
| `pixi run --locked -e dev rust-check`                                               | 0; no test execution                             |
| `pixi run --locked -e dev hooks-check`                                              | 0; repository hook passes                        |
| Stage it and run `git commit -m 'test: verify pre-commit uses check without tests'` | 0; installed source/message hooks pass           |
| `pixi run --locked -e dev test`                                                     | 101; sentinel test fails                         |
| `pixi run --locked -e dev rust-test`                                                | 101; sentinel test fails                         |
| `pixi run --locked -e dev agent-test`                                               | 101; sentinel test fails in the selected package |

Restored source and committed it in the fixture. Added a fixture-only lint task:

```toml
aggregate-sentinel = { cmd = "sh -c 'echo aggregate-sentinel >&2; exit 42'" }
```

Added it to root `lint` dependencies and staged the fixture manifest. Both
`hooks-check` and `git commit -m 'test: reject aggregate check failure'` failed
with the sentinel diagnostic. Earlier equivalent aggregate-failure checks
also asserted stable manifest bytes, index and HEAD on failure. Restored the
manifest; `hooks-check` passed. Both locks remained unchanged. Parsed task
ownership: lint owns check tasks; test owns `test`, `rust-test` and `agent-test`.

## Commit messages and revision sets

For each message, wrote a UTF-8 file whose path contained a space and ran
`pixi run --locked -e dev commit-check "$MESSAGE_FILE"`. Its bytes remained
unchanged on success and failure.

| Input                                                                                                                              | Exit    |
| ---------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `build(hooks): validate commit messages`, blank line, body, blank line, `Refs #6`                                                  | 0       |
| `feat(api)!: change the interface`, blank line, `BREAKING CHANGE: remove the old call`                                             | 0       |
| `revert: restore the previous behavior`                                                                                            | 0       |
| `Merge pull request #123 from example/branch`                                                                                      | 0       |
| `incorrect subject`, empty message, `fixup! feat: change behavior`, `squash! feat: change behavior`, or `Revert "earlier subject"` | 14 each |
| Missing argument to `commit-check`                                                                                                 | 13      |

Used `pixi run --locked -e dev commit-check-range RANGE`:

| Revision input / fixture history                                                                                    | Exit                               |
| ------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Missing range argument                                                                                              | 13                                 |
| `HEAD` with only a valid root commit                                                                                | 0                                  |
| `ROOT..HEAD` after a valid second commit                                                                            | 0                                  |
| `HEAD..HEAD`                                                                                                        | 3                                  |
| `missing-ref..HEAD`                                                                                                 | 23                                 |
| `ROOT..HEAD` or `HEAD` after adding `incorrect historical subject`                                                  | 14                                 |
| `BASE..HEAD` after valid divergent branch commits and `git merge --no-ff valid-side -m "Merge branch 'valid-side'"` | 0                                  |
| Same pattern with an `invalid side history` commit merged from the second parent                                    | 14; invalid side commit identified |

`BASE` was main's commit immediately before each branch was created. Constructed
bad history only in the fixture with
`git -c core.hooksPath=/dev/null commit --allow-empty -m 'incorrect historical subject'`
and the same command with `invalid side history`. Valid commits/merges used
installed hooks. The root and merge cases verify actual Git revision selection.

## Final review and limits

Real-workspace `check`, `test` and `agent-test` passed after the task split;
the latter two each ran the 10 existing CLI tests. The inline environment
refactor preserves parsed configuration and passes locked `check`. Source,
configuration, lockfile hashes and index remained stable during validation.
Reviewed the complete diff, all new files, dependency graph, documentation
ownership, local links/fragments, fences, final newlines and `git diff --check`.

Inspected [issue #7](https://github.com/gleniosp/fleetforge/issues/7) and the
[MachinePulse workflow](https://github.com/gleniosp/machinepulse/blob/main/.github/workflows/pr-checks.yml)
through GitHub's API. #7 owns PR CI; no workflow execution is claimed here.
Existing legacy hooks, custom `core.hooksPath`, interrupted stash restoration,
relocation, fresh package downloads, Ubuntu container and other platforms were
not exercised. Temporary fixture helpers are validation aids; the task reference
owns supported behavior.
