# 2026-10-26 — Independent headless ROS 2 A/B workload delivery

Local review evidence for
[M1-02 (#11)](https://github.com/gleniosp/fleetforge/issues/11).
Source: uncommitted working tree on `feat/11-independent-ros-ab`, based on
`1664879ae89bbcca9913ba2ca5878ff5b1a7d4e6`.

## Delivery and scope review

The [A/B fixture guide](../../examples/ros-workloads/README.md) owns the runtime
inputs, concrete counter/health protocol and commands. Each release has its own
manifest, lock, canonical descriptor and complete application/probe files.
Payload hashes cover all five runtime input files. A increments by 1 and B by
2; health observes that difference through nonce-correlated ROS messages and
checks the actual lifecycle service and current workload identity. A's inputs
remain available alongside B.

`ros-workloads-test` is a Linux-only test task composed into `device-test`, so
the existing Ubuntu 24.04 device CI job will invoke it. Root host checks and
dependencies retain their host matrix. The fixture installs separate copied
workspaces and obtains activation through host-installed Pixi. It does not add
ROS or Python dependencies to the root environment. The two runtime locks have
the same package set but separate ownership/installation prefixes. Their exact
versions and reference execution evidence are in
[experiment 0002](../experiments/0002-ros-workload-runtime.md).

Manual local review covered all new application/fixture source, manifests,
descriptor fields and file sets, the resolved package identities/dependency
edges, task routing and documentation changes. B's main/probe match A's; only
the common module's release ID and counter step differ. The schema example
fixtures remain illustrative and unchanged. No agent deployment path trusts
these unsigned examples. No upstream report has been submitted.

## Validation performed

| Command/check                                                                                                             | Result                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Reference Docker build/run from the [fixture guide](../../examples/ros-workloads/README.md#run-the-bounded-demonstration) | Pass on Ubuntu 24.04 with Pixi 0.83.0, Python 3.14.10 and real ROS 2 Jazzy                                                       |
| `pixi run --locked -e device device-test`                                                                                 | Pass: 10 existing agent CLI tests and the real A/B fixture on native Linux x86_64                                                |
| Final reference run after strengthening negative assertions                                                               | Pass: neighbor test observes an actual identity-mismatching reply; inactive test observes the lifecycle service's inactive state |
| `pixi run --locked -e host format`                                                                                        | Pass                                                                                                                             |
| `pixi run --locked -e host check`                                                                                         | Pass: formatter and hook-configuration checks                                                                                    |
| `bash -n examples/ros-workloads/verify.sh`                                                                                | Pass                                                                                                                             |
| Descriptor schema/canonical bytes, exact payload set, sizes and SHA-256                                                   | Pass for A and B                                                                                                                 |
| Python source parsing                                                                                                     | Pass for all workload/fixture Python files                                                                                       |
| `git diff --check`                                                                                                        | Pass                                                                                                                             |

The reference fixture tested real counter deltas and exact output identity,
fresh random nonce exchange, independent installed prefixes/domains, wrong
endpoint/domain, deliberately misrouted neighbor, live inactive lifecycle,
reactivation, stopped workload, restart with fresh instance identity and a
fault-injected wrong counter delta with matching identity. It checked source
release snapshots before/after and absence of generated source `.pixi` output.

The final negative assertion changes were verified in the reference container;
the earlier canonical native run exercised the same runtime and cases. Runtime
payloads and their hashes were unchanged between those runs. No additional Rust
build/lint rerun was needed for these task/document changes; the existing agent
tests ran through the aggregate. Remote CI has not run for this working tree.

The following manual descriptor review uses the original schemas. It ran with
host Python 3.14.4, jsonschema 4.19.2 and referencing 0.36.2; those review tools
are not runtime or contributor setup requirements. The descriptors contain
only ASCII keys/strings and bounded integers, for which the sorted compact
encoding below matches the contract's JCS bytes. This is not a general JCS
implementation or the future production release checker.

```sh
python3 - <<'PY'
import ast, hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
root = Path.cwd()
schemas = root / 'docs/specs/schemas'
registry = Registry().with_resources(
    (p.as_uri(), Resource.from_contents(json.loads(p.read_bytes())))
    for p in schemas.glob('*.json')
)
validator = Draft202012Validator(
    {'$ref': (schemas / 'release.schema.json').as_uri()}, registry=registry
)
for release in sorted((root / 'releases').iterdir()):
    raw = (release / 'release.json').read_bytes()
    value = json.loads(raw)
    validator.validate(value)
    assert raw == json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    actual = {p.relative_to(release).as_posix() for p in release.rglob('*')
              if p.is_file() and p.name != 'release.json'}
    assert [f['path'] for f in value['files']] == sorted(actual)
    for item in value['files']:
        data = (release / item['path']).read_bytes()
        assert len(data) == item['size']
        assert hashlib.sha256(data).hexdigest() == item['sha256']
for p in list((root / 'releases').rglob('*.py')) + list((root / 'examples/ros-workloads').glob('*.py')):
    ast.parse(p.read_bytes(), filename=str(p))
print('PASS: descriptor schema/canonical bytes/payloads and Python syntax')
PY
```

Relative file/heading links, fences and final newlines were also checked in the
changed Markdown owners. Documentation and protocol review was textual; no
new Mermaid diagram or UI rendering was involved.

## Dependency provenance review

The initial review produced a `runtime-provenance.json` inventory recording
every resolved package's name/version/build, archive URL, declared
license, upstream source URL and any `info/licenses` locations present in its
extracted package metadata. Exact archive hashes remain in each release lock.
The separate inventory was later removed; see the
[2026-10-27 follow-up](#dependency-review-follow-up--2026-10-27).
It was derived from:

```sh
pixi list --manifest-path releases/ros-counter-a-v1/pixi.toml --json
```

Upstream URLs and license-text locations were then inspected in the matching
archives' `info/about.json` and `info/licenses/`. Both release locks select the
same 207 packages. Of these, 204 declare licenses; the other three are
metadata-only `ros-jazzy-*` aliases for the corresponding licensed `ros2-*`
packages. All non-alias packages supply an upstream URL in metadata. License
texts were present under extracted `info/licenses/` for 90 packages. Absence
there does not establish absence from every archive/payload path.

Direct dependency terms were checked against Python's
[3.14.10 LICENSE](https://github.com/python/cpython/blob/v3.14.10/LICENSE),
rclpy's [Apache-2.0 LICENSE](https://github.com/ros2/rclpy/blob/jazzy/LICENSE),
std_msgs' [Apache-2.0 LICENSE](https://github.com/ros2/common_interfaces/blob/jazzy/std_msgs/LICENSE),
and lifecycle_msgs' Apache-2.0 package metadata in the
[rcl_interfaces source](https://github.com/ros2/rcl_interfaces/tree/jazzy/lifecycle_msgs).
The new application/fixture code is original FleetForge source; no upstream
source, package archive or installed environment is vendored or modified.

Transitive license metadata includes Apache/MIT/BSD/PSF terms, GPL/LGPL tools
and libraries, GCC runtime exceptions, and EPL components. Local installation
and execution is the intended use of this delivery. Packaging these runtimes
would also redistribute their transitive tools. Under
[THIRD_PARTY.md](../../THIRD_PARTY.md), that delivery must collect the actual
license/NOTICE material and meet the applicable source/notice requirements;
this source-only delivery does not claim a completed binary redistribution
audit. The findings above, including missing extracted license texts, identify
checks needed for that review.

## Remaining limits

The workloads are unsigned until #86; production integrity/provisioning belongs
to #13. Fresh offline installation and package-byte retention remain #14.
There is no fleet agent/authority deployment or recovery implementation here.
The [experiment](../experiments/0002-ros-workload-runtime.md) records the bounded
transitive-tooling handoff and runtime/platform limits. #12 adds Ruff/mypy and
the broader Python workload test suite. The working tree is left for maintainer
review, without staging, committing or publication.

## Documentation and script naming follow-up — 2026-10-26

Expanded the workload guide around the reason for A/B and actual health checks,
with short explanations when fixture, probe, nonce and dependency terms first
appear. Added a [glossary](../product/glossary.md) for quick lookup and links to
the detailed owners. The release walkthrough keeps its progressive examples
and now distinguishes runnable workloads from document review fixtures.
The workload guide also explains the package provenance inventory's review role
and why execution does not consume that JSON file.

The inventory explanation describes the state on 2026-10-26; the
[2026-10-27 follow-up](#dependency-review-follow-up--2026-10-27) records its removal.

Renamed `verify.sh` to [`run-demo.sh`](../../examples/ros-workloads/run-demo.sh)
and `verify.py` to [`check_workloads.py`](../../examples/ros-workloads/check_workloads.py).
The earlier command records above retain their original names. Current task,
Docker entrypoint and reproduction links use the new names. The shell script
still prepares the independent environments; the unchanged Python driver checks
the actual ROS processes. No release payload, lock, descriptor or digest changed.

Validation after renaming passed:

- `bash -n examples/ros-workloads/run-demo.sh`.
- `pixi run --locked -e device ros-workloads-test`, including all positive and
  negative ROS checks through the renamed entrypoint.
- The reference Docker build/run in the updated workload guide, including the
  renamed container entrypoint and Python driver.
- Relative Markdown file/heading links, fences, final newlines and diff whitespace.
- `pixi run --locked -e host format` and `pixi run --locked -e host check`.

## Dependency review follow-up — 2026-10-27

Removed `examples/ros-workloads/runtime-provenance.json` to avoid maintaining a
second package inventory alongside the release locks. The locks retain package
identities, archive URLs, hashes and declared licenses. The review findings and
their collection method remain in this journal. Updated the workload guide,
glossary and third-party policy links to point to those findings.

A future delivery that distributes packaged environments must collect the
inventory, license texts and notices for its actual distribution inputs.

Validation of the working tree based on `dd49fa4`: host `format` and `check`
passed, as did relative Markdown link/anchor checks and `git diff --check`.
Manual diff review confirmed that only the inventory and its documentation
changed.

## Self-contained Docker demo — 2026-10-27

Working tree based on `07dfadee975b131caf4bbc5a6bcde259c2771191`.
The reference image now supplies Pixi itself, replacing the host-executable
mount used in the original run. Docker is the only host tool required for the
container path. The workload guide distinguishes direct Linux execution from
Docker, provides Bash/zsh and PowerShell commands, and selects `linux/amd64`
explicitly for both build and run.

The Dockerfile copies the unmodified `/usr/local/bin/pixi` from the official
`ghcr.io/prefix-dev/pixi:0.83.0` image, pinned to index digest
`sha256:3dce86c6e87371c58035aa41b09f2b56ca8f011722320551e0c2bfc1c59da5fb`.
Its purpose is preparing and launching the demo's locked environments.
Pixi's upstream source and BSD-3-Clause terms are available at
[v0.83.0](https://github.com/prefix-dev/pixi/tree/v0.83.0) and its
[LICENSE](https://github.com/prefix-dev/pixi/blob/v0.83.0/LICENSE).
The existing Ubuntu base digest and CA-certificate installation remain in place.

The build and run commands in the
[experiment's reproduction section](../experiments/0002-ros-workload-runtime.md#reproduce)
passed on the recorded Linux x86_64 host. Only the repository was mounted,
read-only. The bundled executable reported Pixi 0.83.0 and SHA-256
`50571451e96f4a82cf675cd83baaf66fff9b718f0aaf153900b9faf4c29bd401`, matching
the original binary. The full demo passed A/B health, identity, lifecycle,
domain/endpoint isolation, stopped/stale processes, wrong behavior and source
preservation checks. macOS, Windows, the PowerShell commands and amd64 emulation
were not executed; those configurations follow Docker's documented platform
support and remain unverified for this fixture.

Host `format` and `check`, relative Markdown links/anchors, fences/final
newlines and `git diff --check` passed. Manual diff review covered the image
inputs, documented commands and evidence updates.

## Python engineering review — 2026-10-27

Working tree based on `a6760f6b4e4ea334aeec1ecfd544eb8260c5eddc`.
Reviewed both releases' `common.py`, `main.py` and `health.py`, the demo driver,
lifecycle helper and Bash bootstrap using the python-engineering skill.
Added explicit identity/callback/process/environment types, focused docstrings,
consistent imports/formatting and argparse usage errors. ROS contexts now enter
cleanup even if node construction fails; empty lifecycle service results fail
with an actionable message.

Wire decoding now explicitly rejects nested values, duplicate fields,
nonstandard JSON constants and invalid Unicode, including escaped surrogates.
Decoder recursion failures are translated to the same validation-error path.
The initial nested-input regression showed that this Python 3.14 decoder accepts
1,500 nested arrays; no decoder crash was reproduced on the pinned runtime.
Explicit flat-object validation makes rejection independent of that limit.

Process cleanup tolerates an exit between checking the process and signalling
its group, and still waits to reap it. Probe subprocess timeouts become
retryable startup failures; each startup probe gets at most the remaining
startup budget. Final startup errors retain the last failure and its cause.

Added `test_helpers.py` with ten deterministic regressions. OS signalling,
subprocess errors and the monotonic clock are replaced only at those boundaries;
the existing driver still checks real ROS processes. The bootstrap runs the
helper suite through A's installed interpreter before the ROS driver. These
focused regressions use standard-library unittest to retain the demo's existing
dependency footprint. Project-wide pytest/lint/type tooling remains #12's scope.

Both unsigned candidate descriptors were refreshed for the reviewed payload
bytes. Release locks and manifests are unchanged. The current digests are in
[experiment 0002](../experiments/0002-ros-workload-runtime.md#setup-and-inputs).
This is a refinement of the unmerged fixture delivery; published release
ID/digest bindings must remain immutable.

Validation passed:

- Ten helper regressions, both in the review Python environment and through the
  reference Docker demo.
- The full Docker reproduction command from experiment 0002, including all
  existing positive and negative ROS cases and source-preservation checks.
- The descriptor/schema/canonical-byte/payload and Python syntax command above,
  plus manual checks that A/B main/probe bytes match and `common.py` differs only
  in release ID and counter step.
- `bash -n examples/ros-workloads/run-demo.sh`.

Ad hoc review tools were provisioned with Pixi 0.83.0, without changing root
dependencies or locks. The following commands reproduce the focused static
checks (run from the repository root):

```sh
pixi exec --spec 'ruff=0.17.3' --spec 'mypy=2.4.0' --spec 'python=3.14.10' ruff check --select E4,E7,E9,F,I,UP,B --target-version py314 --config 'lint.isort.known-first-party=["common","check_workloads"]' examples/ros-workloads releases/ros-counter-a-v1/app releases/ros-counter-b-v1/app
pixi exec --spec 'ruff=0.17.3' --spec 'mypy=2.4.0' --spec 'python=3.14.10' ruff format --check --target-version py314 examples/ros-workloads releases/ros-counter-a-v1/app releases/ros-counter-b-v1/app
for scope in examples/ros-workloads releases/ros-counter-a-v1/app releases/ros-counter-b-v1/app; do
  pixi exec --spec 'ruff=0.17.3' --spec 'mypy=2.4.0' --spec 'python=3.14.10' mypy --python-version 3.14 --follow-imports=skip --ignore-missing-imports --check-untyped-defs --disallow-untyped-defs "$scope"
done
```

Ruff checks/import ordering and format checks passed. Mypy checked each of the
three scopes separately, including all nine Python files. Unavailable ROS
import types are treated as external boundaries; this is not complete static
verification of rclpy/generated ROS APIs. Their actual execution passed in the
reference container. macOS, Windows and emulation were not rerun or certified.
Host `format` and `check`, relative Markdown links/anchors, fences/final
newlines and `git diff --check` passed after the documentation updates.
