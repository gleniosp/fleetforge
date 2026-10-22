# Bootstrap exit verification

- **Date:** 2026-10-22
- **Delivery:** [M0-09, issue #9](https://github.com/gleniosp/fleetforge/issues/9).
- **Requirement:** [MVP-01](../product/requirements.md#mvp-01--engineering-foundation).
- **Source:** `2c21afea621cdb5068b13b25473c8daa981ba4cd`, the merged M0
  foundation on `main`. Documentation for this delivery is the working tree on
  `docs/9-verify-bootstrap-exit`, based on that revision.

## Purpose and reproduction

Verify the complete documented contributor workflow using a fresh Git clone,
empty tool caches and the reference Ubuntu 24.04 userspace. This is routine
integration verification under [ADR 0003](../adr/0003-bounded-decisions-and-evidence.md),
using the existing [host-prerequisite Dockerfile](../../experiments/pixi-toolchain/Dockerfile).
The earlier [toolchain experiment](../experiments/0001-pixi-toolchain.md)
owns the detailed lock-drift and inherited-lint failure evidence.

From the repository root, with Docker and Pixi 0.82.1 installed:

```sh
docker build --tag fleetforge-toolchain-evidence:issue-9 experiments/pixi-toolchain
```

Run the following complete walkthrough. The container mounts source and the
Pixi executable read-only, clones Git objects without local hardlinks, and
checks out the exact revision above. It does not mount host environments,
package caches or user Git configuration, and passes no authentication settings.
The Docker image contains Git and CA certificates, with no Rust, C compiler or
contributor tools.

```sh
docker run --rm -i \
  --mount type=bind,src="$PWD",dst=/source,readonly \
  --mount type=bind,src="$(command -v pixi)",dst=/usr/local/bin/pixi,readonly \
  --env PIXI_NO_CONFIG=true \
  --env PIXI_NO_PROGRESS=true \
  --env PIXI_CACHE_DIR=/tmp/pixi-cache \
  --env CARGO_HOME=/tmp/cargo-home \
  --env GIT_CONFIG_NOSYSTEM=1 \
  --env GIT_CONFIG_GLOBAL=/tmp/bootstrap.gitconfig \
  fleetforge-toolchain-evidence:issue-9 bash -euxo pipefail <<'BOOTSTRAP'
export PATH=/usr/local/bin:/usr/bin:/bin
for tool in rustup rustc cargo cc gcc ld python python3 prek cz; do
    if command -v "$tool"; then
        printf 'Unexpected host tool: %s\n' "$tool" >&2
        exit 1
    fi
done
test ! -e "$PIXI_CACHE_DIR"
test ! -e "$CARGO_HOME"
test ! -e /root/.cache/prek
cat /etc/os-release
uname -m
getconf GNU_LIBC_VERSION
git --version
dpkg-query -W ca-certificates
pixi --version
sha256sum /usr/local/bin/pixi

git config --global --add safe.directory /source/.git
git clone --no-local /source /tmp/fleetforge
cd /tmp/fleetforge
git checkout --detach 2c21afea621cdb5068b13b25473c8daa981ba4cd
git rev-parse HEAD
test ! -e .pixi
test ! -e target
test -z "$(git status --porcelain)"
git ls-files -z | xargs -0 sha256sum > /tmp/tracked-before.sha256

pixi install --locked -e dev
pixi install --locked
pixi run --locked -e dev rustc --version
pixi run --locked -e dev cargo --version
pixi run --locked -e dev cargo fmt --version
pixi run --locked -e dev cargo clippy --version
pixi run --locked -e dev prek --version
pixi run --locked -e dev cz version
pixi run --locked -e dev check
pixi run --locked -e dev test
pixi run --locked build
pixi run --locked agent-run
pixi run --locked agent-run -- --help
pixi run --locked agent-run -- --version

pixi run --locked -e dev hooks-install
test -x .git/hooks/pre-commit
test -x .git/hooks/commit-msg
pixi run --locked -e dev hooks-check
printf 'docs: verify bootstrap exit\n' > /tmp/valid-message
printf 'invalid bootstrap subject\n' > /tmp/invalid-message
pixi run --locked -e dev commit-check /tmp/valid-message
if pixi run --locked -e dev commit-check /tmp/invalid-message; then
    echo 'Invalid commit message unexpectedly accepted' >&2
    exit 1
else
    test "$?" -eq 14
fi
pixi run --locked -e dev commit-check-range \
  d8d45730251ed6b403b5c431e1b13d45813af3a4..9add1e6f8eebc02abb3c9bd422ac2d75750b7a99

git ls-files -z | xargs -0 sha256sum > /tmp/tracked-after.sha256
cmp /tmp/tracked-before.sha256 /tmp/tracked-after.sha256
git diff --exit-code
git diff --cached --exit-code
test -z "$(git status --porcelain)"
sha256sum pixi.lock Cargo.lock
echo 'PASS: fresh clone, locked installs, checks, tests, build, CLI, hooks, commit validation and tracked-file stability'
BOOTSTRAP
```

The commit range is the actual proposed history from merged PR #122, excluding
its synthetic merge commit, matching the CI contract. Invalid-message rejection
uses a disposable message file and creates no commit. Hook installation affects
only the disposable clone's `.git/hooks`.

## Environment and observed results

The walkthrough completed with exit 0 and the final `PASS` line. The container
used Ubuntu 24.04.5 x86_64, glibc 2.39, Git 2.43.0 and
`ca-certificates 20260816ubuntu0.24.04.1`. The host was Ubuntu 26.04.1 x86_64,
kernel `7.0.0-38-generic`, Docker 29.7.2. Containers share that host kernel.

The Dockerfile pins Ubuntu to
`sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac`.
The existing Git/CA prerequisite image layer was reused; no Pixi environment,
Cargo build output or package cache was present in it. Apt repositories remain
live inputs when rebuilding that layer. The separately mounted Pixi 0.82.1
executable had SHA-256
`37dc14ed94ed45dafd89f3bb3db95d42fb2063d303c5523a7652b5d93449e9b2`.
Installed tools reported Rust/Cargo 1.98.1, rustfmt 1.9.0-stable,
Clippy 0.1.98, prek 0.5.6 and Commitizen 4.19.2.

| Check | Result |
| --- | --- |
| Fresh clone and cache/tool absence | Passed before installation; no host Rust, C compiler, Python, prek or Commitizen |
| Separate locked dev/default installation | Both succeeded from the committed lock with initially empty caches |
| `check` | Formatting, Clippy with denied warnings and hook configuration validation passed |
| `test` | All 10 CLI integration tests passed; the binary unit-test target contains zero tests |
| `build` and three CLI invocations | Passed; diagnostic reported `fleetforge-agent 0.1.0 (x86_64-linux; bootstrap diagnostic)`, help/version matched the documented interface |
| Hook installation and `hooks-check` | Both hook shims executable; all-file repository check passed |
| Commit validation | Valid message and PR #122's actual proposed range passed; invalid subject rejected with exit 14 |
| Tracked-file stability | All tracked file hashes matched; index, worktree and untracked-file checks were clean |

The integration suite exercises usage errors, extra/repeated options,
non-UTF-8 arguments, closed stdout and Linux `/dev/full` output/error failures
as well as successful commands. These were the existing delivered tests;
bootstrap verification adds no artificial test target or package.

Both source lockfiles retained these hashes:

```text
e131282acc751ab8bb41821f01f7160254580ff45a3febcd7cb0fadcf9b059e7  pixi.lock
0bdbd3f77349171917b2f8568c86b123306747a32dd0f9ae7b2fd7df00752396  Cargo.lock
```

The initial container clone was rejected by Git's ownership safeguard because
the source mount belongs to the host user while this disposable container runs
as root. A command-scoped `safe.directory` setting did not reach the upload-pack
process. The final walkthrough writes one exact-path exception for
`/source/.git` to a disposable container Git configuration; host and source Git
configuration are unchanged. It then succeeds from a new container with empty
caches. Docker image building and GitHub CLI log download also initially hit
the workspace sandbox's restrictions on their user-cache writes; rerunning
those specific operations with environment approval succeeded.

## Hosted CI comparison

Inspected the completed [PR #122 run, 39779909246](https://github.com/gleniosp/fleetforge/actions/runs/39779909246)
and its ordinary step logs:

```sh
gh run view 39779909246 --repo gleniosp/fleetforge \
  --json headSha,status,conclusion,jobs,url,event
gh run view 39779909246 --repo gleniosp/fleetforge --log
```

The event's proposed head was
`9add1e6f8eebc02abb3c9bd422ac2d75750b7a99`; merging it produced the local
verification revision `2c21afea621cdb5068b13b25473c8daa981ba4cd`.
The hosted **Repository checks** job and every validation step succeeded.
Its logs show locked dev/default installation with Pixi 0.82.1, commit-range
validation, all-file hooks, the same 10 passing CLI tests, the default build
and clean tracked-file checks. The local walkthrough reproduces those task
results and additionally exercises tool inspection, documented CLI invocation,
hook installation and invalid-message rejection. The committed
[workflow](../../.github/workflows/pr-checks.yml) disables setup caching and
uses Ubuntu 24.04. The local container explicitly verifies absent host tools
and empty caches before installation; hosted runners contain preinstalled tools.

The [CI delivery record](2026-10-22-github-actions.md#hosted-failure-validation-and-restoration--2026-10-22)
contains the independently published formatting, lint, test and commit-message
failure runs and successful restoration. Those failure injections were not
repeated for this integration check. The Checks API returned HTTP 403 for this
credential; the Actions run/job API and downloadable logs were accessible and
supplied the observations above.

## M0 delivery and scope review

Read live M0 issues, milestone exit criteria, native blockers and merged PR
metadata on 2026-10-22. Issue #9's blockers #7/#8 are delivered on `main` by
PRs #121/#122. Verified all merge commits below are ancestors of the tested
revision. Issue #1 is the historical initial-publication exception under the
[working agreement](../working-agreement.md#review-commits-and-publication).

| Delivery | Merged evidence |
| --- | --- |
| Initial publication #1 | [Foundation journal](2026-10-19-foundation-design.md), `192cde37219bc6c04c09a7777406482e8d99a219` |
| Architecture baseline #85 | [PR #115](https://github.com/gleniosp/fleetforge/pull/115), `dbbe2e09a1f8d88dcfe6d42a125bd565688f3ff7` |
| Working agreement/skills #2 | [PR #116](https://github.com/gleniosp/fleetforge/pull/116), `8492da06dab19c6424842c16a40d6ef03b05a80b` |
| Locked toolchain #3 | [PR #117](https://github.com/gleniosp/fleetforge/pull/117), `7ea5ceb0026740fb6c680e32164a16c92e0c1c3f` |
| Diagnostic executable #4 | [PR #118](https://github.com/gleniosp/fleetforge/pull/118), `c8fc745b0eed2ae295edd9c0ae0f37c2f95d2b44` |
| Canonical tasks/editor defaults #5 | [PR #119](https://github.com/gleniosp/fleetforge/pull/119), `83eb8d934afa4c77ad2a4b3b786423618263333e` |
| Hooks/commit validation #6 | [PR #120](https://github.com/gleniosp/fleetforge/pull/120), `4c9b7716f81c70b0f06de947f5487cbdf4d57f2e` |
| Hosted PR validation #7 | [PR #121](https://github.com/gleniosp/fleetforge/pull/121), `d8d45730251ed6b403b5c431e1b13d45813af3a4` |
| Licensing/contributor safety #8 | [PR #122](https://github.com/gleniosp/fleetforge/pull/122), `2c21afea621cdb5068b13b25473c8daa981ba4cd` |

Reproduce the GitHub delivery inspection with:

```sh
gh issue list --repo gleniosp/fleetforge --milestone 'M0 — Repository bootstrap' \
  --state all --limit 100
gh api repos/gleniosp/fleetforge/milestones/1
gh api repos/gleniosp/fleetforge/issues/9/dependencies/blocked_by \
  --jq '[.[] | {number,state}]'
gh api 'repos/gleniosp/fleetforge/pulls?state=closed&per_page=100' \
  --jq '.[] | select(.number >= 115 and .number <= 122) | {number,merged_at,merge_commit_sha}'
for pr in 115 116 117 118 119 120 121 122; do
  merge=$(gh pr view "$pr" --repo gleniosp/fleetforge --json mergeCommit --jq .mergeCommit.oid)
  git merge-base --is-ancestor "$merge" 2c21afea621cdb5068b13b25473c8daa981ba4cd
done
```

Manual scope review against MVP-01, ADR 0001, the task reference, root manifests,
source/tests, guides, roadmap and traceability found:

- One implemented Cargo package with a real diagnostic CLI and process-level
  regression tests; no empty crates, database, network service, ROS workload,
  frontend or placeholder product runtime.
- Each Pixi task invokes a real tool or aggregates implemented checks/builds;
  the package-free `test` feature owns real Cargo test tasks. Rust is the only
  essential direct tool dependency; prek and Commitizen serve contributor
  validation. Cargo has no external dependencies at this revision.
- Root/default owns build/run; dev composes contributor checks/tests. The
  task reference owns invocation contracts and the working agreement owns
  selection/review/commit/publication. Skills and navigation route to those
  owners. GitHub owns live issue/milestone state; the roadmap and traceability
  link to it without copying progress checklists.
- The historical milestone wording that #85 is the next task is satisfied by
  its merged architecture delivery. The current README distinguishes the
  implemented engineering foundation from planned fleet operation; the guide
  limits verified setup to Linux x86_64 with Ubuntu 24.04 reference userspace.

[Traceability](../traceability.md) links this evidence for maintainers and
reviewers. The [development guide](../guides/development.md) adds the clone step,
identifies verified Pixi 0.82.1, and replaces stale licensing and
hosted-verification references with the delivered state. The README and guide
keep historical verification reports out of the contributor setup path.

## Learning, limits and handoff

The integrated workflow demonstrates why locked environment installation,
source checks, tests, builds and commit validation remain distinct checks.
`--locked` preserves declared inputs and rejects stale resolution; it does not
provide downloaded package bytes. The existing native Rust package supplies
the linker prerequisites, so this clean setup needs no extra direct compiler
package. A successful bootstrap diagnostic verifies contributor execution;
fleet lifecycle behavior retains its own delivery and acceptance evidence.

Consulted the latest official [Pixi install reference](https://pixi.prefix.dev/latest/reference/cli/pixi/install/),
[environment variables](https://pixi.prefix.dev/latest/reference/environment_variables/)
and [Cargo build reference](https://doc.rust-lang.org/cargo/commands/cargo-build.html).
Checked `pixi install --help` and `pixi run --help` against installed Pixi 0.82.1
for locked/no-config options; the walkthrough exercised those options with
Cargo 1.98.1. No package declaration or lock changed.

This verifies online installation in a disposable root-owned Ubuntu userspace
with the recorded host kernel. Pixi was preinstalled and mounted; its installer
was not tested. The clone used local Git transport and carried no credentials;
GitHub HTTPS authentication, fork permissions and an independent contributor's
account were not exercised. The cached Docker prerequisite layer, CA store,
host kernel, Git and Pixi executable are outside the project lockfiles.
Other distributions/architectures, older glibc, non-root permissions, fully
offline installation and bit-identical binaries remain unverified. The future
ROS runtime, agent lifecycle, security boundaries and scale claims receive no
runtime evidence from this task.

This record covers the merged foundation revision; the current documentation
changes still need their normal PR check after publication. Issue #9 and M0
remain open for maintainer review and the authorized merge/closure sequence.

## Local documentation review

Used host Python 3.14.4 for this inline inspection, separate from the supported
contributor toolchain. It checks local file targets, LF/final newlines, balanced
Markdown fences and the shell syntax of every reproduction block in this record:

```sh
python3 - <<'PY'
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

paths = [Path(p) for p in (
    "README.md", "docs/guides/development.md", "docs/traceability.md",
    "docs/journal/2026-10-22-bootstrap-exit.md",
)]
for path in paths:
    text = path.read_bytes().decode("utf-8")
    assert text.endswith("\n") and "\r" not in text, path
    assert sum(line.startswith("```") for line in text.splitlines()) % 2 == 0, path
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        url = urlsplit(target)
        if not url.scheme and url.path:
            assert (path.parent / unquote(url.path)).exists(), (path, target)
journal = paths[-1].read_text()
blocks = re.findall(r"^```sh\n(.*?)^```$", journal, re.MULTILINE | re.DOTALL)
for block in blocks:
    subprocess.run(["bash", "-n"], input=block, text=True, check=True)
print(f"PASS: {len(paths)} documents and {len(blocks)} shell blocks")
PY
pixi run --locked -e dev hooks-check
git diff --check
git diff --exit-code HEAD -- Cargo.toml Cargo.lock pixi.toml pixi.lock \
  apps/agent .github/workflows/pr-checks.yml prek.toml .cz.toml
```

All commands passed. The host hook run initially required environment approval
for prek's user-cache log, then passed. Manually checked local heading fragments
and requirement references, reviewed the complete three-file change including
this new record, and compared source/lock/task/workflow bytes with the tested
revision. No Mermaid source changed; rendered documentation layout was not
inspected. Hooks validate the current implemented Rust/configuration scopes;
Markdown content received the explicit inspection and manual review above.

After local review on 2026-10-22, retained the evidence link only in
traceability and removed it from the README and development guide. Repeated
the inline documentation inspection and `git diff --check`; both passed.
