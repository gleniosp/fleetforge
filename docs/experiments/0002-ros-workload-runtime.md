# Experiment 0002 — Locked headless ROS 2 Jazzy workloads

- **Date:** 2026-10-26; container and Python review refreshed 2026-10-27
- **Owner:** [M1-02 (#11)](https://github.com/gleniosp/fleetforge/issues/11),
  [MVP-02](../product/requirements.md#mvp-02--reproducible-software-releases)
- **Result:** Real A/B lifecycle/message health works in independent Pixi
  runtimes on the Ubuntu 24.04 Linux x86_64 reference container.

This report records a runnable example, or **fixture**, and the evidence from
its execution. Its **health probe** is a small program that checks the running
application's actual behavior. For the purpose and a guided introduction, read
the [workload guide](../../examples/ros-workloads/README.md#why-two-versions-of-a-counter);
the [glossary](../product/glossary.md) provides quick term lookups.

## Question and stopping condition

Can a minimal RoboStack/Pixi runtime run the required headless Jazzy Python
workloads, provide activation variables for direct process spawning, and verify
fresh ROS behavior/identity without a system ROS install or custom interface
build?

Start with rclpy and standard messages rather than a desktop/ros-base bundle or
a custom colcon-built service. A managed lifecycle node plus standard String
challenge/reply topics can carry the full fresh challenge (**nonce**) and
identity without building new interfaces. Stop after independent locked A/B installation, active lifecycle
and observed counter deltas, identity/domain/endpoint failures, inactive/stopped
failures and a wrong-algorithm failure. Offline preparation is #14's question;
trust enforcement is #86's delivery.

## Sources and version compatibility

Consulted the latest official
[RoboStack setup guide](https://robostack.github.io/GettingStarted.html),
[Jazzy package index](https://robostack.github.io/jazzy.html),
[Pixi manifest reference](https://pixi.prefix.dev/latest/reference/pixi_manifest/)
and [shell-hook reference](https://pixi.prefix.dev/latest/reference/cli/pixi/shell-hook/).
RoboStack recommends Pixi and warns against mixing system ROS activation into
its Python environment. Its current Jazzy packages use a shared distro mutex;
the lock selects matching Jazzy builds.

The installed Pixi **0.83.0** help exposes `shell-hook --json`, `--locked`,
explicit `--manifest-path`, and `run --clean-env`. The implementation uses those
supported options rather than newer manifest syntax. The JSON shell-hook output
contains `environment_variables` and `activation_scripts`; the former includes
the variables resulting from package activation. The fixture uses that map to
spawn Python directly with the appropriate AMENT/Python paths. It does not
evaluate shell-hook text.

The official Jazzy
[rclpy lifecycle implementation](https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/lifecycle/node.py)
and [lifecycle Python example](https://github.com/ros2/demos/blob/jazzy/lifecycle_py/lifecycle_py/talker.py)
define managed publisher activation and lifecycle services. The hosted ROS API
pages returned an access-denied page during research, so the matching upstream
Jazzy source was consulted instead. The fixture's actual ROS execution below
establishes compatibility for the locked builds.

## Setup and inputs

Source is the uncommitted working tree on `feat/11-independent-ros-ab`, based on
`a6760f6b4e4ea334aeec1ecfd544eb8260c5eddc` for the Python review run.
The container setup refresh used the working tree based on
`07dfadee975b131caf4bbc5a6bcde259c2771191`.
The original runtime checks used the working tree based on
`1664879ae89bbcca9913ba2ca5878ff5b1a7d4e6`. The versioned inputs are the two
[`releases/`](../../releases/) directories and the
[`examples/ros-workloads/`](../../examples/ros-workloads/README.md) fixture.
Descriptors enumerate/hash their five payload files, including each independent
manifest and lock. Both locks currently have SHA-256:

```text
cbeadb5841e0b9810c74730c48d100a393cf57419883e902ad11234467da1adb
```

The reviewed unsigned fixture descriptor digests are:

| Release            | Descriptor SHA-256                                                 |
| ------------------ | ------------------------------------------------------------------ |
| `ros-counter-a-v1` | `364fe087c62211108ec6c8f7e78e401484a754887759d74c1d8c54e9c6075d38` |
| `ros-counter-b-v1` | `612427c670b261529be31a92807bfe450ea60efca60c0e1e7f12b6426b6a984e` |

| Input/component             | Observed version                                                 |
| --------------------------- | ---------------------------------------------------------------- |
| Host                        | Ubuntu 26.04.1 x86_64, Linux `7.0.0-38-generic`                  |
| Docker daemon               | 29.9.2                                                           |
| Reference image             | Ubuntu 24.04, pinned digest in the fixture Dockerfile            |
| Pixi                        | 0.83.0, copied into the image from its pinned official container |
| Python                      | 3.14.10                                                          |
| rclpy                       | 7.1.12                                                           |
| std_msgs                    | 5.3.8                                                            |
| lifecycle_msgs              | 2.0.4                                                            |
| Fast DDS ROS implementation | `ros2-rmw-fastrtps-cpp` 8.4.4                                    |
| ROS distro mutex            | 0.20.0, Jazzy build                                              |

Pixi executable SHA-256:
`50571451e96f4a82cf675cd83baaf66fff9b718f0aaf153900b9faf4c29bd401`.
The reference execution used Docker on Linux with Ubuntu 24.04 container
userspace. Its image installs CA certificates from live apt repositories and
copies `/usr/local/bin/pixi` from
`ghcr.io/prefix-dev/pixi:0.83.0`, pinned to index digest
`sha256:3dce86c6e87371c58035aa41b09f2b56ca8f011722320551e0c2bfc1c59da5fb`.
The binary hash above matches the host binary used in the original run.
It mounts only source read-only, with no host executable, Python, ROS
environment, package cache or installed environment.
The first release installs with an initially empty container cache; B installs
into another fresh prefix using the container's populated cache. Both use
`--locked`; this does not test offline installation or two independent cold
downloads.

The four explicit runtime packages are Python (entrypoint interpreter), rclpy
(ROS APIs), std_msgs (wire messages) and lifecycle_msgs (state/service types).
Python and lifecycle_msgs also arrive through rclpy's own dependencies
(**transitively**); their direct
pins expose the application's runtime requirements. There are no direct build,
test, compiler, colcon, desktop or root-workspace ROS dependencies.

## Reproduce

From the repository root with Docker capable of running `linux/amd64`
containers (Bash/zsh commands):

```sh
docker build --platform linux/amd64 --tag fleetforge-ros-evidence:issue-11 examples/ros-workloads
docker run --rm --platform linux/amd64 \
  --mount type=bind,src="$PWD",dst=/source,readonly \
  fleetforge-ros-evidence:issue-11
```

The [workload guide](../../examples/ros-workloads/README.md#run-in-docker)
also provides PowerShell commands. The image supplies Pixi, so no host Pixi
installation is needed. This follows the official
[Pixi container guidance](https://pixi.prefix.dev/latest/deployment/container/).
Explicit `linux/amd64` build/run flags select the fixtures' existing platform;
[Docker's platform documentation](https://docs.docker.com/build/building/multi-platform/)
describes Linux container execution and amd64 emulation on ARM hosts.
macOS, Windows and emulated execution were not tested here.

[`run-demo.sh`](../../examples/ros-workloads/run-demo.sh) contains the copy/install
commands; [`check_workloads.py`](../../examples/ros-workloads/check_workloads.py) contains the
activation, process/probe deadlines, fault cases and source snapshots. The
normal fixture chooses independent ROS domains for A, B and subsequent attempts
and a fresh random endpoint namespace for each instance. It fixes DDS to the
already transitively installed `rmw_fastrtps_cpp`, with localhost-only discovery.
The processes have controlled environments, disabled user-site/bytecode writes,
and disposable log/data paths. Every probe receives a fresh 256-bit nonce.

## Observations

The original and refreshed container runs returned exit 0. The Python review
run also passed ten helper regressions before the real ROS checks. These cover
bounded flat JSON parsing, Unicode/constants, process-exit races and startup
probe timeout/retry budgets. The refreshed run
used the image's bundled Pixi with only the source repository mounted.
A and B each installed **207 packages** in
different prefixes. Summing the lock metadata gives **131,045,432 bytes** of
compressed package archives for one package set. The runtime/ABI and actual
probe JSON were printed by the fixture. Distinct manifests/locks currently
resolve equal package sets; installed environments and input ownership remain
independent.

| Check                  | Observed outcome                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------ |
| Real A behavior        | Lifecycle is active; two nonce-correlated ROS replies differ by 1; output is `counter-step-1`          |
| Real B behavior        | Independent lifecycle node replies with delta 2; output is `counter-step-2`                            |
| Identity               | Replies match release ID, descriptor digest, current process instance and fresh probe nonce            |
| Wrong endpoint         | A live old process cannot satisfy a probe for a fresh random instance                                  |
| Misrouted neighbor     | Routing A's probe to B's actual domain/endpoint fails its response identity check                      |
| Wrong domain           | A's endpoint is unavailable from a different ROS domain                                                |
| Inactive lifecycle     | ROS transition to inactive succeeds; the process remains alive and health fails                        |
| Reactivation           | ROS transition back to active restores actual healthy replies                                          |
| Stopped/stale attempts | Health fails after stop and for the old attempt while a new A process runs                             |
| Wrong algorithm        | A child with matching identity but an injected increment of 2 fails with `counter delta 2, expected 1` |
| Input preservation     | All source release bytes match the initial snapshot; no source `.pixi` is created                      |

The final output was:

```text
PASS: independent A/B environments, real ROS behavior, fresh nonce/identity, lifecycle/domain/endpoint isolation, retained unchanged release inputs
```

The initial reference run used a shared domain for A/B to stress private
endpoints. It passed, but the normal fixture was then aligned with the accepted
independent-domain policy. The final run verifies independent domains and
deliberately misroutes only the negative neighbor probe. No package or
activation compatibility failure required a runtime workaround.

## Transitive tooling handoff

The resolved runtime includes CMake, generators, pytest, flake8 and other
build/test packages through upstream run dependencies. This is a footprint
limitation, not an execution failure. For example, the locked metadata contains:

```text
ros-jazzy-rclpy -> ros2-rclpy -> ros2-builtin-interfaces
  -> ros2-rosidl-core-runtime -> ros2-rosidl-generator-py
  -> ros2-ament-cmake -> cmake
ros2-rosidl-generator-py -> ros2-ament-cmake-flake8 -> ... -> flake8
```

A minimal reproducer is the independently owned A manifest/lock. Inspect its
unmodified dependency metadata without a source build:

```sh
pixi list --manifest-path releases/ros-counter-a-v1/pixi.toml --json
```

For an upstream report to [RoboStack](https://github.com/RoboStack/robostack),
attach those inputs, Pixi 0.83.0, `linux-64`, the versions above, and the observed
`depends` edges. Expected improvement: runtime packages retain the generated
Python/type-support files without requiring code-generation and lint/test tools
at run time. Assess whether the dependencies are intentional before proposing a
recipe split. This report has not been submitted upstream. There is no local
dependency override or package-stripping workaround. M1 workload maintainers
own the footprint review; remove this limitation only after an upstream runtime
dependency split is available and locked clean ROS health validation passes.

## Decision, limits and revisit conditions

Use the minimal pinned Python/rclpy/standard-message manifests and direct spawn
with Pixi-produced activation variables for these fixtures. The
[release contract](../specs/releases.md) and
[workload guide](../../examples/ros-workloads/README.md) describe the concrete
behavior. No new architectural framework or custom interface build is needed.

This demonstrates functional health on the reference userspace and current
kernel. It does not prove all Linux/glibc combinations, ARM64, macOS/WSL device
runtimes, physical hardware, hostile ROS participants, production authentication,
privilege isolation, recovery or offline installation. The descriptors are
unsigned; a production reader must reject them until #86 supplies valid
signatures and trusted provisioning. The package lock's virtual-package floor
is a resolver assumption, not a claim that older hosts were exercised.

Revisit after Pixi, RoboStack mutex/ABI, Python, middleware or reference-image
changes; an activation failure; a broader platform target; or an upstream
runtime dependency split. #12 owns further Python tooling/tests; #13/#86 own
production input/trust checks; #14 owns cached fresh offline preparation.
