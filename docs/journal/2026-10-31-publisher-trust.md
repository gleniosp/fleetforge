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

JSON Schema and lightweight parsed objects remain sufficient; no independently
maintained Pydantic model/schema layer is needed. `cryptography` is a direct host
tooling dependency for established Ed25519 primitives, bounded to `>=46,<51` and
locked to 50.0.2. The solve adds CFFI 2.1.1, pycparser 3.12 and Python ABI support
where needed, and reuses existing OpenSSL. Binary Conda packages avoid adding a
host compiler requirement. All three existing developer platforms remain in the
lock; no device runtime platform scope changed.

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
