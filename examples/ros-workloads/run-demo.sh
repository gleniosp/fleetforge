#!/usr/bin/env bash
# An unsigned local fixture. No authority/agent deployment path invokes this.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
pixi_executable=$(command -v pixi)
fixture_root=$(mktemp -d "${TMPDIR:-/tmp}/fleetforge-ros-XXXXXX")
trap 'rm -rf -- "$fixture_root"' EXIT

# Immutable source releases stay untouched; each copy owns its generated .pixi.
for release in ros-counter-a-v1 ros-counter-b-v1; do
  cp -R -- "$repo_root/releases/$release" "$fixture_root/$release"
  "$pixi_executable" install --locked --manifest-path "$fixture_root/$release/pixi.toml"
done

# The fixture uses A's Python standard library, with no host Python/pytest needed.
"$pixi_executable" run --locked --clean-env \
  --manifest-path "$fixture_root/ros-counter-a-v1/pixi.toml" \
  python -B "$repo_root/examples/ros-workloads/check_workloads.py" \
  "$pixi_executable" "$fixture_root" "$repo_root"
