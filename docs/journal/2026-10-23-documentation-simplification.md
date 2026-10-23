# Documentation simplification and first-run verification

- **Date:** 2026-10-23
- **Delivery:** [M0-13 (#128)](https://github.com/gleniosp/fleetforge/issues/128).
- **Source:** working tree on `docs/128-simplify-project-documentation`, based on
  `9c25e54e101d45f154c196c13fd72970ee49cbee`. No implementation/configuration or
  lockfiles changed.

## Scope and review

The README now owns minimum prerequisites and a clone/install/run path for the
bootstrap diagnostic, with an explicit warning sign and host support limits.
The development guide owns contributor workflows; the task reference explains
selection and operational caveats, linking exact definitions to configuration.
The documentation map and agent guidance establish current-state documentation,
with history in journals/experiment evidence and current rationale retained in
ADRs. ADR 0001 is shortened around ownership and rationale. Following maintainer
review, creation/update metadata is retained: ADR 0001 reflects this delivery
date, and ADRs 0002–0003 retain their existing update dates.

The task guide's issue-introduction narrative is removed; the
[canonical-task](2026-10-21-canonical-tasks.md),
[hook](2026-10-21-hooks-and-commits.md) and
[CI](2026-10-22-github-actions.md) journals retain delivery evidence. The obsolete
one-time initial-publication exception is removed from the working agreement;
the [task-delivery journal](2026-10-20-task-delivery.md) retains that context.
Ongoing authorization/review rules are unchanged. Existing historical journals
and experiment reports are preserved.

Manual review covered the documentation map, requirements, architecture,
ADRs, roadmap/traceability, contribution and community policies, and agent
instructions against their owning contracts. The completed toolchain experiment
is removed from the architecture's unresolved-question table; future networking
is described as extending the planned protocol rather than existing software.
Traceability includes #128. Follow-up local review removed its historical
preamble, placed bootstrap evidence links in the MVP-01/NFR-03 rows, and kept
complete-MVP verification owners #45/#48 in the MVP-11 row. Detailed product/security/recovery constraints remain
in their owners, and the three requested README sections remain intact.

## Upstream compatibility review

Consulted current official [Pixi run](https://pixi.prefix.dev/latest/reference/cli/pixi/run/),
[install](https://pixi.prefix.dev/latest/reference/cli/pixi/install/),
[lock](https://pixi.prefix.dev/latest/reference/cli/pixi/lock/),
[update](https://pixi.prefix.dev/latest/reference/cli/pixi/update/),
[manifest](https://pixi.prefix.dev/latest/reference/pixi_manifest/),
[environment](https://pixi.prefix.dev/latest/workspace/multi_environment/) and
[installation](https://pixi.prefix.dev/latest/installation/) references, plus
[Cargo build](https://doc.rust-lang.org/cargo/commands/cargo-build.html) and
[workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html).
Checked `pixi --version`, `pixi run --help`, `pixi install --help` and
`pixi update --help` against installed Pixi 0.82.1. The locked install and argument
forwarding used below passed on that version. No package/version changes or new
package-manager behavior are introduced. The version-specific Pixi documentation
URL was unavailable; compatibility is grounded in installed help and execution,
not an assumption that every latest option exists in 0.82.1.

## Clean README walkthrough

Built the existing [Dockerfile](../../experiments/pixi-toolchain/Dockerfile)
with its pinned Ubuntu image. Its prerequisite layer was cached; this did not
reuse runtime environments or package caches in the test container.
The following reproduces the run from the repository root with Docker and
Pixi 0.82.1 installed:

```sh
docker build --tag fleetforge-toolchain-evidence:issue-128 experiments/pixi-toolchain
docker run --rm -i \
  --mount type=bind,src="$PWD",dst=/source,readonly \
  --mount type=bind,src="$(command -v pixi)",dst=/usr/local/bin/pixi,readonly \
  --env PIXI_NO_CONFIG=true --env PIXI_NO_PROGRESS=true \
  --env PIXI_CACHE_DIR=/tmp/pixi-cache --env CARGO_HOME=/tmp/cargo-home \
  --env GIT_CONFIG_NOSYSTEM=1 \
  --env GIT_CONFIG_GLOBAL=/tmp/quickstart.gitconfig \
  fleetforge-toolchain-evidence:issue-128 bash -euxo pipefail <<'QUICKSTART'
export PATH=/usr/local/bin:/usr/bin:/bin
for tool in rustup rustc cargo cc gcc ld python python3 prek cz; do
    if command -v "$tool"; then exit 1; fi
done
test ! -e "$PIXI_CACHE_DIR"
test ! -e "$CARGO_HOME"
cat /etc/os-release
uname -m
getconf GNU_LIBC_VERSION
git --version
pixi --version
dpkg-query -W ca-certificates
sha256sum /usr/local/bin/pixi
git config --global --add safe.directory /source/.git
git clone --no-local /source /tmp/fleetforge
cd /tmp/fleetforge
git checkout --detach 9c25e54e101d45f154c196c13fd72970ee49cbee
test -z "$(git status --porcelain)"
test ! -e .pixi
test ! -e target
cp /source/README.md README.md
git ls-files -z | xargs -0 sha256sum > /tmp/tracked-before.sha256
pixi install --locked
pixi run --locked agent-run
pixi run --locked agent-run -- --help
pixi run --locked agent-run -- --version
test "$(target/debug/fleetforge-agent)" = 'fleetforge-agent 0.1.0 (x86_64-linux; bootstrap diagnostic)'
test "$(target/debug/fleetforge-agent --version)" = 'fleetforge-agent 0.1.0'
test ! -d .pixi/envs/dev
sha256sum --check --quiet /tmp/tracked-before.sha256
QUICKSTART
```

The fresh clone used the read-only local repository with `--no-local`, then
checked out the exact base revision and overlaid the proposed README. This
avoids publishing unreviewed work; it validates the documented commands against
identical runtime/configuration inputs. It does not test cloning from GitHub or
installing Pixi itself. No host user configuration, credentials, environments or
package caches were mounted.

Observed Ubuntu 24.04.5 LTS x86_64, glibc 2.39, Git 2.43.0, CA certificates
`20260816ubuntu0.24.04.1`, and Pixi 0.82.1 (binary SHA-256
`37dc14ed94ed45dafd89f3bb3db95d42fb2063d303c5523a7652b5d93449e9b2`).
All commands exited 0. The default invocation printed
`fleetforge-agent 0.1.0 (x86_64-linux; bootstrap diagnostic)`;
help listed usage/options and version printed `fleetforge-agent 0.1.0`.
No dev environment was installed; tracked-file hashes were unchanged after
installation/invocation. The container began without the host tools listed above
and empty Pixi/Cargo caches. It used network access for package installation.

## Local validation

```sh
pixi run --locked -e dev hooks-check
pixi run --locked -e dev test
pixi run --locked build
pixi run --locked -e dev rustc --version
pixi run --locked -e dev cargo --version
git diff --check
```

All passed: prek's repository check, 10 CLI integration tests and the workspace
build. Tool versions were rustc 1.98.1 (`48a229cea`, 2026-09-01) and Cargo 1.98.1
(`797e8a9bc`, 2026-08-05). Initial sandbox attempts could not write prek's log
and Docker builder metadata; the same commands passed with approved access.

A temporary Python helper checked relative Markdown links/fragments, final
newlines and paired fences. The inline reproduction below includes its complete
source; it is a delivery review helper, not supported project tooling. It checks
Git-tracked Markdown plus new journal entries and does not fetch external URLs
or parse arbitrary HTML/Markdown extensions. It passed for 42 Markdown files
and 287 relative links/fragments, with no errors.

```sh
python3 - <<'PY'
from pathlib import Path
import re
from urllib.parse import unquote
import subprocess
root = Path.cwd()
files = [root / name for name in subprocess.check_output(['git', 'ls-files', '*.md'], text=True).splitlines()]
files += [p for p in (root / 'docs/journal').glob('*.md') if p not in files]
errors = []
count = 0
for source in files:
    text = source.read_text()
    if not text.endswith('\n'):
        errors.append(f'{source.relative_to(root)}: missing final newline')
    if len(re.findall(r'^```', text, re.M)) % 2:
        errors.append(f'{source.relative_to(root)}: unbalanced code fences')
    for match in re.finditer(r'\[[^\]]*\]\(([^)\n]+)\)', text):
        href = match.group(1)
        if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', href):
            continue
        path, _, fragment = unquote(href).partition('#')
        target = (source.parent / path).resolve() if path else source
        count += 1
        if not target.exists():
            errors.append(f'{source.relative_to(root)}: missing {href}')
        elif fragment and target.suffix == '.md':
            slugs = []
            for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', target.read_text(), re.M):
                heading = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', heading)
                slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
                base, n = slug, 0
                while slug in slugs:
                    n += 1
                    slug = f'{base}-{n}'
                slugs.append(slug)
            if fragment not in slugs:
                errors.append(f'{source.relative_to(root)}: missing fragment {href}')
print(f'Checked {len(files)} Markdown files and {count} relative links/fragments.')
print('\n'.join(errors) if errors else 'No errors.')
raise SystemExit(bool(errors))
PY
```

## Limits

This verifies the bootstrap entry point on the reference Ubuntu userspace, not
other hosts, agent deployment platforms, ROS runtime support, or fleet operation.
The container shares the host kernel. No hosted CI was run for this uncommitted
delivery; existing runtime checks passed locally. Mermaid source was unchanged;
rendered layout was not inspected. Manual review checked the newcomer path
README → development guide and contributor path CONTRIBUTING → development/task
guides → working agreement without requiring configuration details up front.
