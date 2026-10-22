# Locked PR checks

- **Date:** 2026-10-22
- **Delivery:** [M0-07, issue #7](https://github.com/gleniosp/fleetforge/issues/7).
- **Source:** Working tree on `ci/7-locked-validation-github-actions`, based on
  `4c9b7716f81c70b0f06de947f5487cbdf4d57f2e`.
- **Contracts:** [PR checks](../guides/development.md#pr-checks),
  [task reference](../guides/tasks.md#hooks-and-commit-messages),
  [contribution policy](../../CONTRIBUTING.md#pr-checks-and-maintainer-review),
  [MVP-01](../product/requirements.md#mvp-01--engineering-foundation).

## Final scope and sources

Following maintainer review, the delivery is PR-only. Added
`.github/workflows/pr-checks.yml`, named `PR checks`, with one `Repository
checks` job on hosted `ubuntu-24.04`. It runs for PRs targeting `main` on
opened, synchronize, reopened and ready-for-review events. It has no push
trigger. Superseded runs are cancelled and jobs time out after 30 minutes.

Consulted current official [Pixi Actions integration](https://pixi.prefix.dev/latest/integration/ci/github_actions/),
[Pixi install reference](https://pixi.prefix.dev/latest/reference/cli/pixi/install/),
[GitHub events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request),
[workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
and [protected-branch guidance](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
Checked release tags and action input definitions through GitHub's API:

| Action | Release | Pinned commit |
| --- | --- | --- |
| [checkout](https://github.com/actions/checkout/tree/v7.0.1) | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| [setup-pixi](https://github.com/prefix-dev/setup-pixi/tree/v0.11.2) | v0.11.2 | `ad1da6449d9e506fd127fd67ab2d054a769f6a94` |

Setup installs Pixi 0.82.1 and both environments using `environments: dev default`, `locked: true` and `cache: false`. The documented inputs support the
project's Pixi 0.82.x requirement. Full history supports `PR_BASE..PR_HEAD`
message validation; the synthetic merge checkout remains the source-check
input. The existing Commitizen policy handles actual merge subjects. A PR has
an existing base, so the final workflow needs no new-branch/root selection.

The first draft included main-push handling, custom log files, extra version
reporting and diagnostic uploads. Removed that plumbing after review; ordinary
Actions step logs provide command output and failure diagnostics. Canonical
hooks, tests, builds, commit validation and two tracked-diff checks remain.
No dependency, lock, repository rule or review/merge authority changed.

## Validation environment

Used Docker 29.7.2 with the existing bootstrap image
`fleetforge-toolchain-evidence:issue-3`, ID
`sha256:ae54ac93aa46099ae6077fd67bb744c02350bbf7e5d3f50bf0eb866344bb6f42`.
Its [Dockerfile](../../experiments/pixi-toolchain/Dockerfile) adds Git and CA
certificates to pinned Ubuntu 24.04. Observed Ubuntu 24.04.5, Linux x86_64,
Git 2.43.0, Pixi 0.82.1, Rust/Cargo 1.98.1, prek 0.5.6 and Commitizen 4.19.2.

The initial validation copied source from
`git ls-files --cached --others --exclude-standard -z` into a disposable Git
repository, with an empty home directory and no environments/build outputs.
Mounted only Pixi's binary read-only and ran locked dev/default installs,
hooks, tests and build. All passed; all ten CLI tests succeeded. No host
credentials, environments or caches were mounted. Subsequent cases reused
that fixture's installed tools. Source files and both lockfiles stayed stable.

After simplification, a temporary Python/PyYAML helper extracted every final
workflow `run` block unchanged. Executed them using
`bash --noprofile --norc -e -o pipefail SCRIPT` in the same isolated container:

```sh
/tmp/fleetforge-issue7-tools/actionlint -color .github/workflows/pr-checks.yml
docker run --rm --user 1000:1000 --env HOME=/evidence/home \
  --mount type=bind,source=/tmp/fleetforge-ci-ecwx7kvi,target=/evidence \
  --mount type=bind,source=/home/gleniosp/.pixi/bin/pixi,target=/usr/local/bin/pixi,readonly \
  --workdir /evidence/workspace fleetforge-toolchain-evidence:issue-3 \
  bash /evidence/validate-pr.sh
git diff --check
```

Actionlint v1.7.12 was downloaded to `/tmp` and verified against its upstream
release checksum file. It passed the final workflow. ShellCheck was unavailable.
The fixture driver set `PR_BASE`/`PR_HEAD` to real Git objects created with
`git commit-tree`, disabled system/global Git configuration, and restored valid
source between each independent fault. Final workflow steps produced:

| Input | Result |
| --- | --- |
| Valid proposed commit, hooks, tests, build and stable tree | All pass; ten CLI tests pass |
| Malformed `main` signature: `fn main()->io::Result<ExitCode>{` | Hooks exit 1 with rustfmt diff |
| `let unused_ci_sentinel = 1;` inside `main` | Hooks exit 1 with denied Clippy warning |
| Formatted test that panics with `CI test failure sentinel` | Hooks pass; tests exit 101 |
| Invalid proposed commit subject | Commit check exits 14 |
| Checkout is a synthetic merge with invalid subject; proposed head is valid | Commit check passes; synthetic subject excluded |
| Real `Merge ` commit containing valid side history | Commit check passes |
| Real merge containing an invalid side commit | Commit check exits 14 and identifies the side commit |
| Empty proposed range | Commit check exits 3 |
| Missing base object | Commit check exits 23 |
| Unstaged or staged tracked README change | Stability exits 1 |
| Clean tree/index after restoration | Stability exits 0 |

Also exercised inverse staged/unstaged README changes: stage an injected line,
then restore only worktree content from HEAD. A net-content `git diff HEAD`
misses that case. The separate worktree/index checks reject it. Temporary
fixture commands and raw logs are under `/tmp/fleetforge-ci-ecwx7kvi` for this
local review; they are validation aids rather than supported project tooling.

Reviewed all changed Markdown links/fragments, fences, final newlines, full
workflow/task routing and diff whitespace. Both source lockfiles retain their
original bytes. No source-repository staging or commits occurred.

## Limits at the initial local handoff

At the initial local handoff, no workflow had been published or run on GitHub. Hosted action execution,
actual event payloads, fork workflow approval and cancellation remain
unverified. The fresh-cache Ubuntu container establishes command behavior,
not equivalence to GitHub's hosted runner image. Setup's final multi-environment
inputs are documented; the action itself still needs a hosted run.

After maintainer review/commit/publication, record a successful PR run and
controlled formatting/lint/test/commit-message failures from hosted runs before
claiming issue #7's hosted validation complete. Inspect their ordinary Actions
logs and restore valid inputs. Required-check/review recommendations are in the
contribution policy; repository settings remain maintainer-owned.


## Hosted failure validation and restoration — 2026-10-22

The maintainer authorized committing/pushing deliberate faults and restoring the
working state. Each fault used a separate valid Conventional Commit and was
pushed only after the preceding run completed and its failure logs were
inspected. The hosted workflow produced:

| Case | Source revision | Hosted run | Observed result |
| --- | --- | --- | --- |
| Formatting | `bf20578fb749436e0ce138f81c2b933f10a8d0f3` | [39762257245](https://github.com/gleniosp/fleetforge/actions/runs/39762257245) | failure: Hooks rejected the malformed `main` signature |
| Lint | `eb444758e8c73a23354cc98c57f99122c16fe82a` | [39762534171](https://github.com/gleniosp/fleetforge/actions/runs/39762534171) | failure: Hooks rejected `unused_ci_sentinel` under denied warnings |
| Test | `94955f03c5953771d3c189187f519e68fc94a802` | [39762617179](https://github.com/gleniosp/fleetforge/actions/runs/39762617179) | failure: Hooks passed; tests rejected the deliberate panic |
| Commit message | `a93d9c2edd4c6f967bef3dbcc00b2a15161a54d2` | [39762690839](https://github.com/gleniosp/fleetforge/actions/runs/39762690839) | failure: Commit-range validation rejected an invalid runner-only commit |
| Restored working state | `4d9e0f672f337edc67ffca953664ca0216749fff` | [39762762788](https://github.com/gleniosp/fleetforge/actions/runs/39762762788) | success: Every job step passed |

Formatting changed only the `main` signature to `fn main()->io::Result<ExitCode>{`.
The lint case restored formatting and inserted `let unused_ci_sentinel = 1;`.
The test case removed that variable and appended a formatted test that panicked
with `CI controlled test failure sentinel`. The commit-message case restored
application source and temporarily changed only the workflow's range-check
script: `git commit-tree` created an unreachable child of `PR_HEAD` with subject
`controlled invalid commit message`, and `commit-check-range` checked the base
to that child. It failed with that subject in the log. The invalid commit
existed only inside the runner; every published commit has a valid message.

For each failure, inspected `gh run view RUN_ID --json status,conclusion,headSha,jobs,url`
and `gh run view RUN_ID --log-failed`. Asserted that the job concluded `failure`,
that exactly the expected validation step failed, and that its log contained the
injected diagnostic. The other steps followed normal failure/skip behavior;
the tracked-file stability check still passed. Temporary drivers, JSON receipts
and downloaded failure logs remain under
`/tmp/fleetforge-hosted-fault-validation` for this local review.

Fault commits used command-scoped `git -c core.hooksPath=/dev/null commit` so
the intentionally invalid source could reach hosted validation. This did not
change hook configuration. The restoration commit used normal Git commit
behavior. No force push or published-history rewrite was used.

The restoration run passed checkout, locked Pixi environment installation,
commit-range validation over all published fault/restoration commits, hooks,
tests, build and stability. Confirmed restoration with:

```sh
git diff --exit-code 7b7ad03 HEAD -- apps/agent/src/main.rs .github/workflows/pr-checks.yml pixi.toml pixi.lock Cargo.lock
```

The command returned zero before the documentation commit. The temporary source
and workflow faults are absent from the final PR diff. This hosted evidence
supersedes the initial hosted-verification gap above. Fork workflow approval
and cancellation were not separately exercised.

## Issue synchronization rule

Updated the owning [working agreement](../working-agreement.md#github-state-and-milestone-exit)
to require issue descriptions, acceptance/validation checklists and dependencies
to match the delivered scope when raising/updating a PR. Before final review,
all applicable items require evidenced completion, and each fully delivered
issue requires its own `Closes #<issue-number>` in the default-branch PR body.
GitHub closes issues on merge. Existing root instructions and the PR skill
already require this owner; no policy copy was added to another instruction file.

Reviewed the full branch diff, documentation links/fragments, final newlines and
`git diff --check`. The final documentation commit is validated by the PR's
latest hosted run, linked from its Validation section.
