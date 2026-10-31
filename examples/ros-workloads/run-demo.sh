#!/usr/bin/env bash
# Compose runs this script inside a disposable Linux container.
# An unsigned local fixture. No authority/agent deployment path invokes this.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
pixi_executable=$(command -v pixi)
fixture_root=$(mktemp -d "${TMPDIR:-/tmp}/fleetforge-ros-XXXXXX")
trap 'rm -rf -- "$fixture_root"' EXIT

# Immutable source releases stay untouched; each copy owns its generated .pixi.
for release in ros-counter-a-v1 ros-counter-b-v1; do
  source_root="$repo_root/examples/releases/$release"
  test ! -L "$source_root"
  test ! -L "$source_root/app"
  mkdir -p "$fixture_root/$release/app"
  for file in pixi.toml pixi.lock release.json app/main.py app/common.py app/health.py; do
    test -f "$source_root/$file"
    test ! -L "$source_root/$file"
    cp -- "$source_root/$file" "$fixture_root/$release/$file"
  done
  "$pixi_executable" install --locked --manifest-path "$fixture_root/$release/pixi.toml"
done

# The fixture uses A's Python standard library, with no host Python/pytest needed.
"$pixi_executable" run --locked --clean-env \
  --manifest-path "$fixture_root/ros-counter-a-v1/pixi.toml" \
  python -B "$repo_root/examples/ros-workloads/check_workloads.py" \
  "$pixi_executable" "$fixture_root" "$repo_root"
