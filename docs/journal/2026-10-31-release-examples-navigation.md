# Release examples and documentation navigation

Date: 2026-10-31. Maintainer-requested follow-up to #86.
Source: working tree based on `0598986a1ba33cb7c28a695c47d64ba626f7e11e`.

## Changes

The documentation map now links topic indexes. Product, guides, architecture,
specifications and experiments have short reading lists; ADRs retain numeric
order and journals have a newest-first index. Root navigation links these entry
points rather than listing each document.

Runnable A/B inputs moved from `releases/` to `examples/releases/`. Shared release
conformance data moved from `testdata/releases/v1/` to
`examples/releases/conformance/v1/`, alongside its explanatory README and review
matrix. The README explains fixed expected answers, Python publishing tests,
planned Rust reader tests, and the difference from actual runtime release inputs.
Schema contracts remain under `schemas/`.

Tool defaults, ROS fixture setup/runner, tests, mypy paths and Ruff exclusions
follow the new paths. The provisioner still selects only the A/B folders. All
12 release files and seven conformance JSON files retain their exact committed
bytes, including release IDs, descriptor hashes and runtime locks. Historical
report prose and commands retain their original meaning at their recorded
revisions; file links were repaired. For current commands use the guides.

The main provisioning guide now signs disposable copies, provisions public
publisher bindings separately from release inputs, and verifies signatures and
integrity. Unsigned inspection is an explicit optional section. The guide states
what the standalone ROS demonstration verifies and explains the existing 4 KiB
envelope budget as format policy rather than a cryptographic requirement.

## Validation

Linux x86_64; Pixi 0.83.0, Python 3.14.10, pytest 9.1.1.

- `pixi run --locked -e host python-test`: 102 passed, one ROS test deselected.
- `pixi run --locked -e device ros-workloads-test`: one passed, 102 deselected;
  fresh temporary A/B environments ran real ROS behavior and health checks.
- Manual execution of all four shell command blocks in the
  [provisioning guide](../guides/release-provisioning.md), in order with a fresh
  temporary base replacing the guide's example base: passed. Signed authority
  and device catalogs/checks reported `integrity_only: false`; optional unsigned
  provisioning/checking reported `true`.
- `pixi run --locked -e host python-fix`, `pixi run --locked -e host format` and
  `pixi run --locked -e host check`: passed, including Ruff, strict mypy and
  Prek configuration checks.
- Manual relocation comparison: for every tracked file under the old release
  and conformance data directories, compared its new file bytes with
  `git show 0598986:<old-path>`; all 19 matched after formatting.
- Markdown file targets and edited local fragments checked; diff whitespace
  checked with `git diff --check`. Local review covered executable paths,
  formatting protection, documentation/index content and the moved inputs.

Checks ran on Linux x86_64. Other developer hosts and the reference Docker
container were not rerun. Diagrams in the guide are existing text diagrams;
rendered Markdown layout was not inspected. Offline installation remains #14.
