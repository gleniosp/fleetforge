# 2026-10-27 — Python tooling and ROS workload checks

Local delivery evidence for [M1-03 (#12)](https://github.com/gleniosp/fleetforge/issues/12).
Source: uncommitted working tree on `build/12-python-workload-checks`, based on
`5af08b895d1e4285e7a6c5bb3b3078dfba9b31a8`.

## Delivery and dependency review

The [development guide](../guides/development.md#python-tooling-and-workload-tests)
owns contributor commands; the [workload guide](../../examples/ros-workloads/README.md)
owns the real ROS fixture. All Python tests use pytest. Portable tests run on
host platforms; the marked ROS integration runs on Linux x86_64 and shares its
verification implementation with the standalone demonstration.

| Direct dependency | Pin     | Present role                                                           |
| ----------------- | ------- | ---------------------------------------------------------------------- |
| Python            | 3.14.10 | Shared repository interpreter, matching the releases' language version |
| Ruff              | 0.17.3  | Python formatting and linting                                          |
| mypy              | 2.4.0   | Strict checks of support code and each independent release tree        |
| pytest            | 9.1.1   | Portable and real ROS tests                                            |

Python belongs to shared dependencies, Ruff/mypy to lint and pytest to test.
The root lock resolves all three developer platforms. Manual dependency review
covered mypy's ast-serialize/python-librt/typing dependencies, pytest's runner
dependencies and Python's matching ABI/runtime packages. The interpreter was
already a transitive contributor dependency; the explicit pin replaces root
3.15 selections with 3.14.10. Direct tool license metadata is MIT for
Ruff/mypy/pytest and Python-2.0 for Python. No ROS runtime package enters the
root environments, and accepted releases retain their original manifests,
locks, descriptors and payload bytes.

Compared against MachinePulse revision `36c7e35c3720aad399ed97a003d1b1a8a24c2539`:
its [Ruff policy](https://github.com/gleniosp/machinepulse/blob/36c7e35c3720aad399ed97a003d1b1a8a24c2539/ruff.toml)
uses the same rules and formatting defaults. Its
[mypy policy](https://github.com/gleniosp/machinepulse/blob/36c7e35c3720aad399ed97a003d1b1a8a24c2539/mypy.ini)
is strict; that policy is now applied here. Its import-layout settings are
specific to its packages and are unnecessary for FleetForge's independent
release scripts. Missing upstream ROS typing requires narrowly scoped
exceptions; real ROS tests remain the behavioral evidence.

Configuration was checked against the current official
[Pixi](https://pixi.prefix.dev/latest/reference/pixi_manifest/),
[Ruff](https://docs.astral.sh/ruff/configuration/),
[mypy](https://mypy.readthedocs.io/en/stable/config_file.html) and
[pytest](https://docs.pytest.org/en/stable/how-to/fixtures.html) documentation,
and executed with Pixi 0.83.0. `prek.toml` remains identical to the base revision;
its existing `fix` hook picks up repository-wide Python fixes. Hook policy is
in the working agreement; writing guidance is in `docs/AGENTS.md`.

## Observations and validation

Native Linux x86_64 runs use the pinned tools above. Each independent ROS
runtime contains 207 packages, including Python 3.14.10, rclpy 7.1.12,
std_msgs 5.3.8, lifecycle_msgs 2.0.4 and Fast DDS RMW 8.4.4.

The initial implementation passed 36 Python tests, ten Rust CLI tests and the
real ROS checks natively. The first clean Ubuntu run passed host and Rust
checks/tests but failed with `lifecycle service unavailable`: the control
helper allowed only two seconds for discovery. It now shares the descriptor's
startup budget across discovery and response, with bounded parent headroom.
A missing-service case verifies a clear failure within a 0.2-second budget.
The corrected initial clean run passed setup, checks, all tests and build,
and its before/after SHA-256 source comparison passed.

Following maintainer review, Python moved from lint to shared dependencies,
Prek was restored, mypy became strict, helper tests were converted to pytest
and the real ROS scenario gained a pytest entrypoint. Native validation passed:

- `pixi run --locked -e host python-check`: Ruff and strict mypy pass.
- `pixi run --locked -e host test`: 51 portable cases pass. Parameterization
  reports A/B wire cases individually; the previous assertions are preserved.
- `pixi run --locked -e device ros-workloads-test`: one real ROS scenario passes.

The revised clean Ubuntu run below also passed setup, host checks, all 51
portable cases, device checks, ten Rust tests, the ROS pytest scenario and the
build. The final source/lock checksum comparison passed. Local formatting,
repository fixes/checks, Prek safety checks, Markdown links/fragments and
`git diff --check` passed; `prek.toml` and `releases/` have no diff against the
base revision.

The ROS assertions cover measured A/B deltas, exact release/digest/process/nonce
identity, separate runtimes/domains, wrong neighbors, inactive/stopped/stale
processes and an intentionally wrong counter algorithm. Invalid process
identity, health nonce and descriptor digest produce nonzero exit with no
success output. A temporary untracked Python probe was also rejected separately
by format, lint and type checks for bad indentation, an undefined name and an
incorrect annotated return type; the probe was removed.

### Clean reference reproduction

This streams source into a disposable Ubuntu 24.04 container with Pixi 0.83.0,
without host environments or caches. Git supplies the contributor prerequisite
for hook setup. The final checksum comparison covers all source inputs and locks.

```sh
docker build --platform linux/amd64 --tag fleetforge-ros-evidence:issue-12 examples/ros-workloads
git ls-files --cached --others --exclude-standard -z |
  tar --null -T - -cf - |
  docker run --rm -i --platform linux/amd64 fleetforge-ros-evidence:issue-12 bash -euc '
    mkdir /work
    tar -xf - -C /work
    apt-get update -qq
    apt-get install --yes --no-install-recommends git >/dev/null
    cd /work
    git init -q
    find . -type f -not -path "./.git/*" -not -path "./.pixi/*" -not -path "./target/*" -print0 |
      sort -z | xargs -0 sha256sum > /tmp/source-before.sha256
    pixi run --locked -e host setup
    pixi run --locked -e host check
    pixi run --locked -e host test
    pixi run --locked -e device device-check
    pixi run --locked -e device device-test
    pixi run --locked -e device device-build
    sha256sum --check --quiet /tmp/source-before.sha256
  '
```

## Limits

Native ARM64/macOS execution and remote CI for this working tree have not run;
the locks and CI matrix include them. ROS remains Linux x86_64 only. Mypy does
not validate untyped upstream ROS interfaces. Offline installation, publisher
trust and the deployment engine belong to later deliveries. Changes remain
uncommitted for local review.
