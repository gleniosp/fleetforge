# Contributor hosts and Linux device runtime boundary

- **Date:** 2026-10-23
- **Delivery:** [M0-14 (#130)](https://github.com/gleniosp/fleetforge/issues/130), MVP-01.
- **Current scope:** revised to Windows through WSL2; see the dated scope
  correction below. Earlier native-Windows observations are retained as history.
- **Source:** uncommitted working tree on `build/130-developer-host-portability`,
  based on `362b14fac4ca1ef0dd7d2f12c15cbd7642f8da9a` (updated `main`).

## Scope and decision

Root Pixi default/dev tooling now declares Linux x86_64/ARM64, macOS Intel/Apple
Silicon and Windows x86_64. Requirements, architecture, ADR 0001 and agent
instructions separate those contributor hosts from Linux x86_64 device agents,
workloads and MVP simulation. No operational runtime is implemented by this
change. Future device-only packages/tasks must stay scoped to their components
and runtimes; FUT-08 retains device-platform expansion.

The maintainer requested host-installed Pixi only and a minimum of 0.83, without
an upper version cap. The manifest uses `>=0.83.0`; CI pins 0.83.0 to test that
minimum. The initially downloaded temporary 0.82.1 executable and archive were
removed. Subsequent validation uses global `pixi`, including the read-only host
executable mount in the disposable container. No Pixi executable is installed
inside a project or temporary environment.

Native Rust already supplies Cargo/rustfmt/Clippy and Linux linker dependencies.
The macOS and Windows locked default environments each contain Rust and its
standard library, not a native linker/SDK. The development guide therefore
requires Xcode Command Line Tools or Visual Studio C++ Build Tools/Windows SDK.
No direct dependencies were added. Existing Linux package URLs in both
environments are preserved. Other platforms have their own native package
resolutions, aligned through the existing solve group; lock metadata is also
normalized by the solver.

CI adds five native host jobs and retains the `Repository checks` name as an
aggregate requiring every host job. Commit validation, hooks, tests, build,
diagnostic invocation, cleanup and tracked-file stability run for each host.
These jobs establish contributor portability, not device/runtime integration.
Windows cleanup uses native PowerShell, pins Cargo intermediate/final output
to `target/`, and refuses reparse points including live/dangling junctions.
The Windows safety fixture is included in CI; it was manually inspected here.

## Sources and compatibility

Consulted current official [Pixi manifest](https://pixi.prefix.dev/latest/reference/pixi_manifest/),
[multi-platform configuration](https://pixi.prefix.dev/latest/workspace/multi_platform_configuration/),
[tasks](https://pixi.prefix.dev/latest/workspace/advanced_tasks/),
[locked installation](https://pixi.prefix.dev/latest/reference/cli/pixi/install/),
and [0.83.0 release](https://github.com/prefix-dev/pixi/releases/tag/v0.83.0)
documentation. Checked version-sensitive manifest/task behavior against
`pixi --version`, `pixi lock --help`, actual lock/install/task execution, and
initially the tagged 0.82.1 manifest documentation. The latest docs do not replace
execution evidence for the selected minimum.

Reviewed conda-forge's [Rust package metadata](https://api.anaconda.org/package/conda-forge/rust),
[recipe](https://github.com/conda-forge/rust-feedstock/blob/main/recipe/recipe.yaml)
and [linker activation](https://github.com/conda-forge/rust-feedstock/blob/main/recipe/install-rust.sh),
Rust's [macOS](https://doc.rust-lang.org/stable/rustc/platform-support/apple-darwin.html)
and [Windows MSVC](https://doc.rust-lang.org/stable/rustc/platform-support/windows-msvc.html)
requirements, [Cargo build-directory configuration](https://doc.rust-lang.org/cargo/reference/config.html#buildbuild-dir),
and GitHub's [native runner matrix](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
Native prerequisites outside the lock remain explicit; no virtual-package
requirements were overridden. Lock defaults include Linux/glibc 4.18/2.28,
macOS 13 and Windows 10. These are resolution constraints, not execution proof.

## Local commands and observations

Host: Ubuntu 26.04.1 x86_64, glibc 2.43. Global Pixi 0.83.0; Rust/Cargo 1.98.1,
Prek 0.5.6 and Commitizen 4.19.2. Global Pixi executable SHA-256:
`50571451e96f4a82cf675cd83baaf66fff9b718f0aaf153900b9faf4c29bd401`.
Run from the repository root using the host `pixi`:

```sh
pixi --version
pixi lock
pixi lock --check
pixi install --locked --all
pixi run --locked -e dev check
pixi run --locked -e dev hooks-check
pixi run --locked -e dev test
pixi run --locked build
pixi run --locked agent-run
pixi run --locked agent-run -- --help
pixi run --locked agent-run -- --version
pixi run --locked clean
bash -n experiments/pixi-toolchain/verify.sh
git diff --check
```

All completed successfully: 10 CLI tests passed; formatting, Clippy and hook
configuration passed; all-file hooks passed; the diagnostic printed
`fleetforge-agent 0.1.0 (x86_64-linux; bootstrap diagnostic)`. Cleanup removed
only generated output. Source/lock snapshots were unchanged by validation.
Sandboxed Prek initially could not write its normal log; rerunning with
approved access passed. Some sandboxed Pixi commands warned about read-only
metadata caches; the recorded passing resolution/container checks had the
needed access. An initial 0.82.1 environment-install approval was rejected;
that command did not run. Final installation/validation succeeded with global
0.83.0 after the maintainer clarified the version policy.

Manual/static review compared default/dev Linux package URL lists against the
base lock (equal), manifest/lock/CI platform sets (five, matching), YAML/TOML
parsing, cleanup source, aggregate CI failure propagation, documentation
contracts and affected relative links/fragments. GitHub Actions itself and
PowerShell were not available for native execution on this Linux host.

## Fresh reference userspace

Reproduced with the existing pinned Ubuntu container fixture and the global
host Pixi executable mounted read-only:

```sh
docker build --tag fleetforge-toolchain-evidence:issue-130 experiments/pixi-toolchain
docker run --rm \
  --mount type=bind,src="$PWD",dst=/source,readonly \
  --mount type=bind,src="$(command -v pixi)",dst=/usr/local/bin/pixi,readonly \
  fleetforge-toolchain-evidence:issue-130 \
  bash /source/experiments/pixi-toolchain/verify.sh
```

The first run found the existing fixture omitted the manifest's required
`LICENSE` input. After adding it to the copied inputs, the complete rerun
passed on Ubuntu 24.04.5/glibc 2.39, Git 2.43.0 and CA package
`20260816ubuntu0.24.04.1`. The Docker prerequisite layer was cached; Pixi
environments/package caches and Cargo output were fresh. No host compiler or
contributor tools were mounted. Default/dev each compiled and linked with
Pixi tools; default excluded Prek, Commitizen and Python. Release build and
diagnostic execution passed. Stale Pixi/Cargo locks and injected unsafe Rust
failed as intended, preserving source/lock hashes. The fixture printed its
final `PASS: fresh installs, isolated tool paths, builds, lock rejection,
inherited unsafe lint, source preservation` marker and exited 0.

## Bounded platform and cleanup probes

Native Windows ARM64 was attempted with the same dependency pins. Reproduce
without installing an environment or changing the repository manifest:

```sh
pixi run --locked -e dev python - <<'PYCODE'
from pathlib import Path
import subprocess, tempfile
with tempfile.TemporaryDirectory(prefix='fleetforge-win-arm64-') as work:
    root = Path(work)
    manifest = Path('pixi.toml').read_text().replace(
        '"win-64"]', '"win-64", "win-arm64"]')
    (root / 'pixi.toml').write_text(manifest)
    (root / 'LICENSE').write_text(Path('LICENSE').read_text())
    result = subprocess.run(
        ['pixi', 'lock', '--manifest-path', str(root / 'pixi.toml'), '--dry-run'],
        capture_output=True, text=True)
    print(result.stdout + result.stderr)
    assert result.returncode != 0
    assert 'commitizen 4.19.2' in result.stderr
PYCODE
```

With cache access, global Pixi 0.83.0 failed with `No candidates were found for
commitizen 4.19.2.*` on `win-arm64`. Rust itself has an ARM64 Windows package;
the complete contributor toolchain is the blocker. Native Windows ARM64 is
therefore excluded, rather than claiming an unsolvable supported host. Revisit
when the pinned contributor packages support it, followed by native execution.
Linux ARM64 through a VM/WSL2 is only a possible unverified route, not tested
Windows-native support. No 32-bit or niche architectures were added.

The Unix cleanup probe extracted the actual manifest command and ran it on a
disposable Cargo project with external output overrides and a sentinel:

```sh
pixi run --locked -e dev python - <<'PYCODE'
from pathlib import Path
import os, subprocess, tempfile, tomllib
cmd = tomllib.loads(Path('pixi.toml').read_text())['tasks']['rust-clean']['cmd']
with tempfile.TemporaryDirectory(prefix='fleetforge-clean-') as work:
    root = Path(work)
    (root / 'src').mkdir()
    (root / 'src/main.rs').write_text('fn main() {}\n')
    (root / 'Cargo.toml').write_text(
        '[package]\nname="clean-fixture"\nversion="0.0.0"\n')
    subprocess.run(['cargo', 'generate-lockfile', '--offline'], cwd=root, check=True)
    outside = root / 'outside'
    outside.mkdir()
    keep = outside / 'keep'
    keep.write_text('preserve')
    env = dict(os.environ, CARGO_TARGET_DIR=str(outside),
               CARGO_BUILD_BUILD_DIR=str(outside))
    subprocess.run(cmd, cwd=root, env=env, check=True)
    target = root / 'target'
    target.mkdir(exist_ok=True)
    (target / 'CACHEDIR.TAG').write_text(
        'Signature: 8a477f597d28d172789f06886806bc55\n')
    (target / 'generated').touch()
    subprocess.run(cmd, cwd=root, env=env, check=True)
    assert not (target / 'generated').exists()
    assert keep.read_text() == 'preserve'
    if target.exists():
        target.rmdir()
    for destination in (outside, root / 'missing'):
        target.symlink_to(destination, target_is_directory=True)
        assert subprocess.run(cmd, cwd=root, env=env).returncode == 1
        target.unlink()
    assert keep.read_text() == 'preserve'
PYCODE
```

Passed: absent/ordinary target succeeded; live and dangling symlinks failed
with exit 1; external sentinel survived both environment overrides. Windows
`scripts/test-clean.ps1` (subsequently removed; see scope correction) covers analogous
absence/output/override and live/dangling junction cases in CI. That fixture and
the Windows implementation remain unexecuted locally.

## Limits and review handoff

The five host configurations resolve and have CI definitions. Only Linux
x86_64 ran here. Native Linux ARM64, macOS Intel/Apple Silicon and Windows
x86_64 jobs must run after requested publication; their execution is not
claimed. No CI run was dispatched and no commit/push/PR was created. Branch
protection settings were not changed. Operational agents, ROS, Docker Desktop
behavior on other hosts, cross-compilation and non-Linux device deployment
were not tested or added. Current README/guide support statements preserve
these distinctions; historical Linux-only reports remain historical evidence.

## Scope correction — 2026-10-23, Windows through WSL2

The maintainer selected Ubuntu on WSL2 for Windows contributors. The final
manifest and CI cover four native Linux/macOS platforms; Windows developers
use the Linux tools inside WSL2. Removed `win-64` resolutions, its CI job, and
the two newly added PowerShell cleanup scripts. Earlier five-platform and
Windows-cleanup descriptions above record the initial investigation only;
they do not describe the final configuration. The earlier Windows ARM64 probe
must add `win-arm64` to the current platform list explicitly to reproduce.
WSL-specific integration remains unverified; Linux CI alone does not prove it.

README now states the developer/device distinction briefly and uses a GitHub
WARNING alert matching Machinepulse's presentation. The original experiment
report now clarifies that host `bash -n` was a Linux syntax-only review, not
execution or a general contributor requirement. Full experiment execution
remains inside its disposable Ubuntu container. The task guide explains normal
Cargo build caching, cleanup scope, symlinks and output-directory overrides.

Validation after the WSL2 revision: `pixi lock` removed only Windows package
selections; `pixi lock --check`, `pixi run --locked -e dev check` and
`git diff --check` passed. Parsed TOML/YAML confirmed four matching platforms in
the manifest, both locked environments and CI; both PowerShell files are absent.
Reviewed relative links and corrected the historical link to the removed
Windows fixture. No runtime code changed, so the earlier Linux execution and
cleanup results remain applicable; native macOS/ARM64 and WSL2 execution remain
pending. Issue #130 scope/checklists were updated for WSL2, the README warning,
experiment clarification and cleanup explanation.

## Setup and CI refinement — 2026-10-23

Added root `setup`, routing to dev `hooks-install`. Pixi automatically installs
the selected environment before running that task; no recursive Pixi install
command or extra dependency is needed. Host Git/Pixi/SDK prerequisites remain
manual. A disposable Git checkout copied the current Pixi manifest/lock,
LICENSE and hook configuration, then ran global
`pixi run --manifest-path <checkout>/pixi.toml --locked setup` twice. Both
pre-commit and commit-msg executable hooks existed after each run. The actual
checkout's hooks were not changed. No robot setup task was added before an
operational deployment exists.

CI now runs commit-message validation and repository hooks only on Linux
x86_64. Every native host still installs default/dev, builds, executes tests
and checks tracked-file stability. Removed redundant diagnostic invocation
(the CLI suite already runs it) and optional cleanup of disposable runners.
The task guide owns the single short explanation of cleanup behavior.

Reviewed current official [Pixi run](https://pixi.prefix.dev/latest/reference/cli/pixi/run/)
and [manifest](https://pixi.prefix.dev/latest/reference/pixi_manifest/) docs;
actual setup execution establishes compatibility with global Pixi 0.83.0.
[RoboStack Jazzy](https://robostack.github.io/jazzy.html) and
[rclpy package metadata](https://api.anaconda.org/package/robostack-jazzy/ros-jazzy-rclpy)
list Linux x86_64 and ARM64 packages. This supports considering both device
targets but does not prove an entire locked FleetForge/ROS runtime, health,
offline installation or hardware drivers. No device runtime scope was expanded.
Issue #130 was updated to reflect setup, concise cleanup docs, CI scope and
this bounded platform assessment.

## Validation-scope correction — 2026-10-23

Latest maintainer direction replaces the earlier CI refinement: contributor
tooling/setup/hooks and commit validation now run on all four developer hosts.
The dedicated Linux x86_64 device job owns agent formatting, linting, build and
tests. No standalone agent/demo is started. Current portable source components
do not yet exist; `tooling-check` validates hook configuration and executes
formatter/linter/commit tooling. Add contributor-source validators/tests to that
scope as their components arrive. Device sources must not expand that host
scope implicitly.

Pre-commit separates `tooling-check` and `device-check`. The latter's shell guard
runs `rust-check` only on Linux x86_64; other hosts report an explicit skip.
Contributor CI uses Prek's `SKIP=device-check` to leave device validation to its
separate job. Both hooks passed on Linux amd64. The contributor-only route,
`SKIP=device-check pixi run --locked -e dev hooks-check`, passed with the device
hook skipped. A disposable PATH containing a fake Darwin `uname` and failing
`pixi` proved that unsupported-device hosts skip without invoking device tools.
This tests dispatch behavior, not native macOS execution.

`pixi run --locked -e dev agent-test` passed all 10 tests;
`pixi run --locked build`, `pixi lock --check`, shell syntax and diff whitespace
checks passed. Parsed YAML confirmed host steps have no Linux-only condition,
contain no agent build/test/run commands, the device job uses Ubuntu x86_64,
and the aggregate gate requires both scopes. Native CI execution remains
pending publication; untested hosts/WSL2 are disclosed limits, not a new
all-platform execution prerequisite for issue completion. Required configured
CI checks must pass before merge. No CI success is claimed here.

Future issues #69 and #70 already mentioned ARM64; their scope now explicitly
prioritizes `linux-aarch64` ahead of other device-platform expansions. README,
architecture and FUT-08 agree. This does not activate deferred implementation
or claim current device ARM64 support. Issue #130 tracks the final scope and
records the available-host/local-Linux validation policy.

## Task and native-platform audit — 2026-10-23

Latest scope supersedes the script-based dispatch: removed Intel macOS, leaving
Linux x86_64/ARM64 and Apple Silicon macOS, with Windows through WSL2. Root README
owns the short entry path; the development guide owns host commands and limits.
The task guide owns task scopes and the sole cleanup explanation.

The shared `toolchain` feature contains pinned Rust; `lint` contains Prek and
Commitizen. `host` validates portable tooling/configuration, `dev` composes local
review with a Linux-only native target dependency, and `device` uses a platform-
restricted feature and excludes default tasks. Device component leaves and
check/format/format-check/lint/fix/test/build aggregates compose without repeated
Cargo commands. Unnecessary root wrappers and version-printing checks were
removed; the current portable configuration check is Prek validation, and real
portable component validators will be added with those components. No source
component is silently represented by a version check.

Removed `scripts/device-check.sh` and Prek skip lists. A single generic hook
entry forwards `FLEETFORGE_CHECK_ENV` (default `dev`) to Pixi `check`.
`hooks-check` sets that variable using Pixi 0.83's documented environment-name
template. CI selects `host`; local hooks select `dev`; the separate Linux-only
CI job selects `device`. No hook calls itself, and `check` cannot reach
`hooks-check`. `agent-run` has one toolchain target definition for optional local
bootstrap use; CI still only builds/tests the device app.

Consulted current official Pixi manifest/tasks/installation references and the
0.83.0 task parser/template implementation. Native target tables, restricted
feature platforms, cross-environment dependencies and environment-name templates
were exercised on global Pixi 0.83.0. Initial checks caught a task-name collision
and ambiguous duplicate wrappers; both were removed before final validation.

Pinned conda-forge Rust 1.98.1 metadata/lock: Linux Rust depends transitively on
GCC and a sysroot; macOS Rust depends on its standard library and does not ship
Apple's linker/SDK. The guide therefore uses official Ubuntu APT and Apple
Command Line Tools instructions, then the official Pixi installer. No host
compiler package or Homebrew dependency was added.

Prek was upgraded from 0.5.6 to 0.5.7. Validation used Pixi 0.83.0,
Ubuntu 24.04 CA package `20260816ubuntu0.24.04.1` in the reference container,
and `20260816ubuntu0.26.04.1` on the local Ubuntu 26.04 host.

Passing local checks: host/dev hooks, device check (rustfmt/Clippy/config), all
10 agent tests, device/root build, root format-check and `agent-run -- --version`
forwarding. `fix` intentionally refused the dirty working tree (exit 101),
preserving Cargo's safeguards. Native Apple Silicon/ARM64 and WSL integration
remain unexecuted locally; CI results must be recorded only after a run exists.

The refreshed Ubuntu fixture passed fresh installation of all four environments,
default/dev native linking, release build, CLI invocation, lock-drift rejection,
unsafe-lint rejection and source/lock preservation with Prek 0.5.7. The container
used the existing pinned Ubuntu image and global host Pixi read-only mount;
only the host prerequisite image layer was cached. Actual host APT/macOS SDK
installation commands were reviewed against official docs, not executed on or
used to mutate the maintainer's host.

Final hook routing exposed Pixi's dependency-context behavior when a device
aggregate was reached from dev. Device aggregate edges now explicitly name the
`device` environment, keeping leaf lookup unambiguous across scopes. After that
fix, both `pixi run --locked -e dev hooks-check` and the `host` equivalent passed,
as did direct device check. Resolved task metadata was inspected for cycles;
relative file links and diff whitespace passed. The deleted platform script
has no remaining executable references.

## Final environment simplification — 2026-10-23

Removed `host`: it duplicated dev packages solely to route checks. `dev` now
owns portable contributor tools and `repo-check`; `device` contains only the
Rust/device features and device-check/agent checks/tests. The lock confirms no
Prek, Commitizen or Python in device. `default` owns root `check`, using native
Pixi targets to combine dev repo-check with device-check on Linux x86_64.
Pre-commit directly invokes `pixi run --locked -e default check`; explicit
selection prevents an active dev environment from capturing nested `pixi run`.
No shell dispatcher, platform script, scope variable or Prek skip list remains.
CI validates repo-check/setup/commit tools on developer hosts, and device-check,
tests/build in the device job. The three-environment task graph was checked for
cycles. Device checks and all 10 tests passed locally; lock/diff checks passed.

Removed development's introductory README setup link, eliminating the direct
setup navigation loop. README remains the short entry point; the development
guide owns complete prerequisites and contributor setup.

The experiment base-image digest remains pinned. No host Docker upgrade or
daemon restart was performed by this task.

## Feature ownership and final checklist consolidation — 2026-10-23

Replaced the append-only issue checklist with eight outcome-based criteria,
retaining validation limits and the actual delivered scope. README no longer
repeats the missing-runtime statement or Git/Pixi setup text; prerequisites
are owned solely by the development guide.

Removed the toolchain feature and all environment-owned tasks, task environment
fields, cross-environment dependencies and task-level Pixi dispatch. Rust is
now the default dependency. Default Linux target tables own device commands;
`lint` owns contributor setup/check/hook tasks and its Linux target composes
repo-check with device-check. Dev selects lint; device limits default tooling
to Linux x86_64 without lint dependencies. CLI/CI/Prek select environments
explicitly. Manifest organization, default/named feature choice, task ownership,
explicit environment selection and nonrecursive composition conventions have
one owner in the task guide. Global Pixi 0.83.0 accepted the manifest/lock.

Actual checks after this refactor: dev check and hooks, direct device check and
all 10 agent tests passed. Lock consistency and diff whitespace passed. No new
package versions were needed; native non-Linux execution remains pending CI.

## Three-feature ownership revision — 2026-10-23

Latest direction restores the fixed default/lint/test feature roles. Default
owns shared Rust and Linux device build/run/clean; lint owns checks, formatter,
linter/fix and contributor tooling/setup; test owns agent test execution without
an extra dependency. Dev and device both select lint/test alongside implicit
default; device remains restricted to Linux x86_64. Removed default-feature test
and lint tasks and the redundant device-check aggregate. Linux `check` composes
format-check and lint; component commands remain single definitions.

With global Pixi 0.83.0, lock refresh succeeded; dev check, device check and all
10 device tests passed. Device now includes the requested lint dependencies.
Repo-wide source scope on non-device hosts is awaiting maintainer clarification:
agent is the only source component and earlier direction restricted its source
checks to Linux x86_64. Portable build/format/test placeholders were not added.
This is not a claim that the requested all-host aggregate surface is complete.

## Confirmed host/device scope — 2026-10-23

Maintainer clarified that host-only and device-only features must be isolated,
not merely selected by OS. Replaced dev with host. Default now shares Rust only;
host selects lint/test, device selects device/device-lint/device-test and is
restricted to linux-64. Distinct feature families are necessary to exclude agent
tasks from host even on Linux x86_64. Host check currently validates contributor
configuration; its selected test feature has no suite yet. No fake host build,
format or test command was introduced to stand in for a portable component.
Device retains build/run/clean, source check/format/lint/fix and test aggregates,
composed from agent leaves with no environment routing in task definitions.

Updated README, guide commands, Prek, CI, requirements, ADR and issue #130.
Host hooks never run the agent; CI covers host configuration/setup/commit tools
on all native developer platforms and device check/test/build only on Linux
x86_64. The task graph is acyclic; inspection of resolved Linux task metadata
confirmed no agent tasks in host and all required aggregates in device. Host
check/hooks, device check, all 10 tests and build passed. Lock update removed
dev, added host, and removed host contributor packages from device again.
The prior ambiguity is resolved; non-Linux/WSL execution is still not claimed.

The experiment script now uses default/device for Rust compile/link checks and
host only for Prek/Commitizen tool checks. Docker is observed as 29.9.2 now;
no host upgrade was performed by this task. The previous fixture image was
absent, so its first run failed before executing the script; rebuilding the
existing fixture restored the image, reusing the host prerequisite layer.

The rebuilt clean fixture completed successfully with default/host/device:
fresh locked installation, native compiler/linker paths, separate default/device
builds, host contributor tool invocation, formatting/lints, release/diagnostic
execution, expected stale-lock/unsafe-code failures, and source preservation.
It printed the final PASS marker and exited 0. Current relative file links,
renamed CLI references, CI scope routing, lock consistency and diff whitespace
also passed. CI/native non-Linux/WSL results remain pending, not inferred.

## Shared features with explicit device tasks — 2026-10-23

Latest maintainer direction replaces the separate device feature family with
exactly implicit default, lint and test. Default owns shared Rust and Linux-only
device-build/agent-build/agent-run/device-clean. Lint owns repository check,
format/format-check/lint/fix and setup/hooks, plus Linux-only device-prefixed
source aggregates and agent leaves. Test owns Linux-only device-test/agent-test.
Host and device select the same lint/test features; device restricts linux-64.
Repository check never runs device checks. On Linux, device-prefixed tasks are
visible in host but remain explicitly selected; earlier host task-visibility
assertions describe the prior configuration only.

Taplo 0.10.0 is a new direct lint dependency justified by the requested actual
repository format/format-check/lint/fix behavior for existing TOML metadata.
It is published for all three developer platforms; no runtime dependency was
added. Consulted official Taplo formatting, validation and configuration docs,
then checked installed CLI/help and execution. `.taplo.toml` selects repository
TOML, excludes generated trees, and disables schema/network lookup. Repository
fix composes the formatter's supported corrections and does not pretend to
repair arbitrary invalid documents. Device source remains rustfmt/Clippy.
No Markdown/Python/frontend validation is claimed or added by these tasks.

Repository format and check passed. Parsed TOML values before/after formatting
were compared across all six input files, preserving semantics. A disposable
unformatted fixture failed format-check without edits; format repaired it and
then check passed. Invalid TOML lint failed without edits. Device-check passed;
all 10 device tests and device-build passed. The manifest/lock still validate on
global Pixi 0.83.0; no environment fields occur in task definitions/dependencies.
Relevant guides/contracts/CI/issue #130 were reconciled to the device-prefixed
names. Native non-Linux/WSL/CI execution remains unclaimed until actual runs.

The refreshed Ubuntu fixture installed default/host/device from the new lock
(including Taplo), compiled/linked default/device, executed host tools and the
diagnostic, and passed stale-lock/unsafe-code rejection with source preservation.
It exited 0 with its final PASS marker. The initial external formatting probe
was excluded by the repository include pattern; rerunning inside a disposable
workspace with the same config exercised the actual failure/repair cases.
Taplo sources: [formatting](https://taplo.tamasfe.dev/cli/usage/formatting.html),
[validation](https://taplo.tamasfe.dev/cli/usage/validation.html),
[configuration](https://taplo.tamasfe.dev/configuration/file.html).

## Correction — Prek built-ins replace Taplo (2026-10-23)

Maintainer direction supersedes the preceding Taplo configuration. Removed
Taplo and its config/lock entries. Repository `check` now runs Prek's pre-commit
hooks directly; removed redundant `hooks-check` and host format/lint/fix tasks.
Built-ins validate TOML/JSON/YAML, filename case, merge conflicts, added file
size, whitespace and final newlines. Whitespace/newline hooks use `--check`;
Markdown hard line breaks are preserved. A local hook validates Prek config;
no hook calls `check`, so routing is acyclic. Device tasks are unchanged.

Using global Pixi 0.83.0 and Prek 0.5.7 on Linux amd64, `pixi lock` and
`pixi run --locked -e host check` passed. Installed `prek util list-builtins -v`
confirmed hook/argument support. Focused temporary fixtures rejected malformed
TOML/JSON/YAML, trailing whitespace and missing final newlines without byte
changes, and accepted valid TOML. `git diff --check` passed. This change does
not add native ARM/macOS/WSL2 execution evidence. Official references:
[Prek built-ins](https://prek.j178.dev/reference/built-in-hooks/) and
[CLI](https://prek.j178.dev/reference/cli/).
