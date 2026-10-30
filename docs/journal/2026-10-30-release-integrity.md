# Release integrity and local catalog provisioning

Date: 2026-10-30. Delivery: [#13](https://github.com/gleniosp/fleetforge/issues/13).
Evidence source: working tree on `feat/13-release-integrity-catalog`, based on
`0795a3db1c0662d43c7485d484d85831b6a41ad5`. This is uncommitted delivery evidence.

## Delivered boundary

`tools/releases/catalog.py` validates catalog/request identity, strict canonical
descriptors, repository schemas, file membership/hashes/sizes, safe paths and
regular-file ownership constraints, and manifest/lock consistency. It stages
unsigned A/B fixtures for authority/device inputs with deterministic catalogs,
rejects existing conflicting bindings and preserves valid identical inputs.
The [guide](../guides/release-provisioning.md) owns commands and operational limits.

Host dependencies `jsonschema` 4.26.0 and `referencing` 0.37.0 provide Draft
2020-12 validation and a registry containing only repository schema resources.
Pixi resolved their transitive dependencies in the shared toolchain lock across
all three host platforms; no release runtime manifest or lock changed. Python
3.14.10 and host-installed Pixi 0.83.0 were used on Linux x86_64. The latest
[official lock reference](https://pixi.prefix.dev/latest/reference/cli/pixi/lock/)
and installed `pixi lock --help` agree on `--check`, `--offline` and `--no-config`.
The checker uses these flags on disposable protected inputs with a deadline.

## Validation

Executed on this working tree:

- `pixi run --locked -e host python-test`: 76 passed, one real-ROS test deselected.
  This includes 25 release regressions covering deterministic repeat provisioning,
  source/copy stability, duplicate/noncanonical/oversized JSON, invalid Unicode,
  nesting and number bounds, schema/platform/path rejection, hashes, missing/extra
  files, symlinks/hard links/FIFOs, timing, unknown IDs, conflicting bindings,
  manifest drift with updated descriptor hashes, and rejection before Pixi runs.
- `pixi run --locked -e host format` and `pixi run --locked -e host check`:
  formatting, Prek configuration, Ruff and strict mypy passed. Cache writes required
  sandbox escalation; the initial restricted runs could not write dprint/Prek caches.
- Manual CLI provisioning to a disposable `/tmp` destination produced deterministic
  A/B bindings. The reproducible CLI and source inputs live in the repository;
  temporary output is not a delivery artifact.
- Manual source/diff review, including schema references, task/CI inclusion and
  immutable release input boundaries; `git diff --check` passed.

The A/B descriptor digests observed were respectively
`sha256:364fe087c62211108ec6c8f7e78e401484a754887759d74c1d8c54e9c6075d38`
and `sha256:612427c670b261529be31a92807bfe450ea60efca60c0e1e7f12b6426b6a984e`.

## Limits and handoff

These are integrity results, not publisher authentication or deployment evidence.
#86 must add envelope/keyring verification at the marked stage before payload/Pixi
validation and before a trusted execution path uses these inputs. No install,
activation or ROS process was run for this delivery. #14 still owns actual fresh
offline cache installation. The current adapter deliberately rejects manifest
forms beyond the fixtures' binary Conda subset. Provisioning assumes protected
roots and serialized writers; it does not implement crash-durable runtime records.
Other developer hosts were resolved but not executed locally. CI already includes
the portable tests and host Python checks; no CI result is claimed here.

## Shared schema source and Python annotations

The five release schemas moved without byte changes from `docs/specs/schemas/`
to `schemas/releases/v1/` during local review. The checker and current
documentation now use that source; historical journal commands retain their
original paths. The current checker still requires a checkout. Packaging or
embedding schemas belongs with separately distributed consumers.

Removed unnecessary future annotation imports from the mutable checker and
workload demonstration on Python 3.14. Immutable A/B payloads retain their bytes
and descriptor identities. The canonical encoder now names its safe-integer
bound as `MAX_SAFE_JSON_INTEGER = 2**53 - 1`; validation behavior is unchanged.

## Numeric readability review

Reviewed Python numeric literals across the checker, workload support, tests and
immutable A/B payloads. Named the checker's version 1 input limits separately
from implementation budgets, derived the tree-entry/snapshot bounds, and replaced
ASCII numbers in the nesting scanner with character expressions. Named the
workload helper's identity sizes, output bound and timing budgets with units.
Added short explanations for the ROS domain selection, lifecycle timeout and
representative test-size/install-time values. Values and limit behavior remain
unchanged. Ordinary indices, status/schema values and independent test boundary
inputs remain inline where their context supplies the meaning. Immutable release
payloads remain unchanged; editing them requires new release identities.

The portable suite passed (76 tests, one ROS integration test deselected) after
the checker and helper refactor. Host formatting, Ruff, mypy and diff review passed.
The real ROS integration run was not repeated for this readability change.
