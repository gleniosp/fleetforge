# Fresh offline ROS installation from an isolated Pixi cache

- Date: 2026-10-31
- Issue: [M1-05 (#14)](https://github.com/gleniosp/fleetforge/issues/14)
- Requirements: MVP-02 and the installation foundation of MVP-10
- Source: working tree based on `182fc67dbbc9dc6705085031822bdc69daf22a5c`

## Question and method

Can Pixi prepare an absent B environment using a populated local cache with
external networking disabled, then pass real ROS behavior/health checks? Does
preparation fail clearly when required package data is absent? These positive
and negative outcomes are the stopping condition.

The [Compose fixture](../../examples/ros-workloads/compose.offline.yaml) signs
and verifies disposable A/B inputs, then warms a dedicated workload cache online.
Contributor tooling has a separate cache. Verification runs with
`network_mode: none`, checks that only loopback exists, and requires absent target
`.pixi` directories. It tests an empty cache before installing fresh A/B copies
with `pixi install --locked --offline --no-config` and running the real ROS checker.
The image contains explicitly selected inputs; generated outputs use a disposable
volume. [Usage and cleanup](../../examples/ros-workloads/README.md#fresh-offline-installation-experiment)
own the reproduction commands.

The official [install reference](https://pixi.prefix.dev/latest/reference/cli/pixi/install/)
and [environment variables](https://pixi.prefix.dev/latest/reference/environment_variables/)
document locked installation, offline failure and `PIXI_CACHE_DIR`. Installed
Pixi 0.83.0 help confirms these flags. The experiment validates cache completeness
beyond command compatibility.

## Setup and results

Tested on Linux x86_64 with Docker Engine 29.9.2, Compose v5.6.1 and the pinned
Ubuntu 24.04 image (reported as 24.04.5 LTS), using Pixi 0.83.0.
Both A/B locks have SHA-256
`cbeadb5841e0b9810c74730c48d100a393cf57419883e902ad11234467da1adb`.
Each selects 207 Conda packages totaling 131,045,432 archive bytes; the locks
record their URLs, hashes and sizes. Both select the same package set.
Measured workload cache apparent size was 548,052,850 bytes (`du -sb`), including
extracted packages and metadata; this is not a storage reservation guarantee.

The complete Compose run exited zero:

- Verification had only loopback and no external routes.
- Empty-cache preparation exited nonzero with `failed to fetch` and
  `network access is disabled by offline mode`. This omits all packages, rather
  than testing one damaged archive.
- Fresh A/B environments were installed under independent `.pixi/envs/default`
  paths. Real probes observed `counter-step-1` and `counter-step-2` with matching
  release/process identity and fresh nonces.
- Endpoint/domain isolation, inactive/stopped workloads, stale attempts and wrong
  behavior checks passed. Source release files remained unchanged.
- Runtime versions included Python 3.14.10, rclpy 7.1.12, lifecycle_msgs 2.0.4,
  std_msgs 5.3.8 and rmw_fastrtps_cpp 8.4.4.

Image inspection found exactly 26 selected source files under `/source`.
Compose configuration validation and cleanup passed. The PR workflow runs this
fixture in a parallel Linux x86_64 job; the updated workflow has not yet run on
GitHub.

## Recommendation and limits

Populate a dedicated Pixi cache from approved locks during trusted online setup.
Preserve package data and metadata for offline preparation and recovery; a lockfile
alone does not contain the required bytes. A failed install may leave partial
output, which must never establish readiness.

Evidence covers the same platform, Pixi version and cache path. Cache relocation,
other hosts/emulation, selective corruption, concurrent access, disk exhaustion
and interrupted preparation were not tested. This does not establish authority
connectivity, active A surviving failed B preparation, or the full MVP-10 matrix.
Revisit when Pixi, locks, platform or cache provisioning/storage policy changes.
