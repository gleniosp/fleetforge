# Publisher trust delivery — 2026-10-31

Issue: [#86](https://github.com/gleniosp/fleetforge/issues/86).
Source: working tree based on `471795b87a5766760bb8001bd343841e6a5cc7cb`.

## Delivered behavior

The host checker and provisioner accept an explicit local public keyring and
verify pure Ed25519 over the domain-separated canonical descriptor bytes before
payload/Pixi inspection. The CLI requires a keyring or an explicit integrity-only
choice. Python callers must explicitly supply a keyring or `None` for integrity
inspection. These tools do not install or activate software.

Disposable signing tools create a new host directory and private seed with modes
0700/0600, respectively, and add envelopes without rewriting descriptor/payload
bytes. Existing secrets and envelopes are never overwritten. The guide describes
public binding provisioning, separate authority/publisher roles and manual trust
replacement. Source A/B remain unsigned, with their existing immutable IDs and
bytes. Signing copies using the fixture ID is for disposable demonstrations only.

The original seven JSON contract fixtures moved byte-for-byte from
`docs/specs/fixtures/releases/` to `testdata/releases/v1/`. This is a location
correction for the historical contract journal's reproduction snippet: its
`fixture` variable now refers to the shared directory. Expected vector bytes and
digests were not regenerated. Python tests consume the canonical-byte, digest and
signature-message vectors; the future Rust reader can consume the same files.

## Dependency decision

No detailed comparison of Pydantic V2 with the existing JSON Schema and
lightweight parsed objects was performed. The implementation keeps JSON Schema
as the single release contract and adds no Pydantic dependency. The issue marks
the model-layer question optional; reassess it only if typed models show a
concrete benefit. `cryptography` is a direct host tooling dependency for
established Ed25519 primitives, bounded to `>=46,<51` and locked to 50.0.2. The
solve adds CFFI 2.1.1, pycparser 3.12 and Python ABI support where needed, and
reuses existing OpenSSL. Binary Conda packages avoid adding a host compiler
requirement. All three existing developer platforms remain in the lock; no
device runtime platform scope changed.

Consulted the [official Ed25519 API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/)
and [latest Pixi manifest reference](https://pixi.prefix.dev/latest/reference/pixi_manifest/).
Installed Pixi 0.83.0 accepted the existing feature dependency/task syntax and
resolved the dependency across the project's platforms.

## Validation

On Linux x86_64, Pixi 0.83.0, Python 3.14.10, cryptography 50.0.2 and pytest 9.1.1:

- `pixi run --locked -e host python-test`: 102 passed, one ROS test deselected.
  Includes signed A/B read-only checking and repeat provisioning; CLI key generation,
  signing and checking; rejection of missing/bad/substituted signatures, unknown/wrong
  keys, modified descriptors/payloads, invalid envelope encoding, duplicate/invalid
  keyring entries; required trust selection; protected secret permissions and no
  overwrite; failed provisioning leaves no destination. Negative trust/integrity
  checks assert that Pixi is never invoked.
- `pixi run --locked -e host format` and `pixi run --locked -e host check`:
  formatting, Prek configuration, Ruff and strict mypy pass.
- Manual comparison of all seven moved fixtures against their source revision:
  bytes unchanged. `git diff --check` passes. Manual local diff review includes
  dependency/lock changes, trust selection and rejection order, documentation and
  fixture relocation.

Initial formatting/check attempts encountered read-only global cache paths;
rerunning with authorized cache access completed the checks. This is host evidence:
macOS/ARM64 execution, real ROS integration, production trust provisioning, device
runtime verification and offline installation were not exercised. Offline cache
proof remains #14; the Rust execution reader remains #20.

## Dependency ownership correction

`jsonschema`, `referencing` and `cryptography` are runtime dependencies of the
repository release tools. They and the release tasks now live in the base
dependency/task tables, available to contributor environments without enabling
lint. Managed workloads retain their separate release manifests. The updated
lock also includes these dependencies in the default contributor environment.

## Demo publisher identity

The generated fixture keyring and A/B v1 descriptors use `demo-publisher-1`
in place of `unsigned-demo-publisher`. Source: working tree based on
`f5d3d43fc66895a671f1afd098bfcbb74a828dce`. The maintainer authorized revising
these development examples in place. Only `signing.key_id` changes in each
descriptor.
Workload files, embedded release IDs, runtime manifests and locks are unchanged.

This is a development-example revision authorized before these inputs serve as
published deployment/recovery releases. Existing catalogs and signing fixtures
using the old descriptors must be recreated. The published-release immutability
contract remains in effect. Conformance fixtures and expected vectors are unchanged.

| Release            | Revised descriptor digest                                                 |
| ------------------ | ------------------------------------------------------------------------- |
| `ros-counter-a-v1` | `sha256:3ad63f1c4ec0e8f15f6f70ceeb467471f6eecda4400b75c34af90697cf080cac` |
| `ros-counter-b-v1` | `sha256:15113d835b62ded3288e6f09832a152c9b457b26d9e47177601af7c633067855` |

Validation on Linux x86_64 with the host versions recorded above:

- `pixi run --locked -e host python-test`: 102 passed, one ROS test deselected.
- Manual execution of all four provisioning-guide shell blocks with a fresh
  temporary base: passed with the new publisher ID and revised v1 descriptors.
- Manual comparison with `git show f5d3d43:<path>` confirmed that each descriptor
  changes only its key ID and all other v1 files retain their original bytes.
- `pixi run --locked -e device ros-workloads-test`: one passed, 102 deselected;
  actual ROS behavior and health checks passed for revised A/B v1 descriptors.
- `pixi run --locked -e host python-fix`, `pixi run --locked -e host format`,
  `pixi run --locked -e host check` and `git diff --check`: passed.

Other host platforms and the reference container were not rerun.

## CI correction: physical host temporary paths

[PR #142's macOS ARM64 job](https://github.com/gleniosp/fleetforge/actions/runs/41203974413/job/124545190669)
failed at `ca67edc59191379132a03ec928d23784f83cc02b`: 11 trust tests encountered
`NotADirectoryError` while reopening checker-owned snapshots under `/var/folders`.
The host's `/var` alias points to `/private/var`; strict no-follow traversal
correctly rejects the alias. Linux x86_64/ARM64 host checks and Linux device
checks passed. The aggregate repository check failed because the macOS job failed.

The checker now resolves the host-provided temporary parent before creating its
private snapshot directory. This is independent of OS names and leaves caller
release roots, publisher keyrings and payloads under the existing no-follow
rules. Catalog/request conflicts still reject before temporary storage is used.
Provisioning already creates its staging directory beneath a validated destination
parent and needs no change.

Source: working tree based on `ca67edc59191379132a03ec928d23784f83cc02b`.
Added `test_signed_check_with_symlinked_host_temp`, which configures a real
symlink as Python's host temporary parent on Linux. Valid signed A/B inputs must
pass; missing/invalid signatures must reject before Pixi runs. All cases assert
unchanged input bytes and cleanup of temporary snapshots. The existing
release-root, payload and directory-link rejection tests remain enabled.

Validation on Linux x86_64, Python 3.14.10 and pytest 9.1.1:

- `pixi run --locked -e host python -B -m pytest tools/releases/test_trust.py -k symlinked_host_temp`:
  three failed with `NotADirectoryError` before the fix; three passed after it.
- `pixi run --locked -e host python-test`: 105 passed, one ROS test deselected.
- `pixi run --locked -e host python-fix`, `pixi run --locked -e host format`,
  `pixi run --locked -e host check` and `git diff --check`: passed.

Native macOS confirmation requires a CI run after publication of this correction.
The Linux regression reproduces the filesystem condition; it is not native macOS
execution evidence. ROS runtime tests were not rerun because workloads and their
runtime inputs are unchanged.
