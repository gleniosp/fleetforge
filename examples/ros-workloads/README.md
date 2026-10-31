# Headless ROS 2 A/B workload fixtures

Before FleetForge can switch software on a robot, we need to establish that the
software can run in its own environment and that a health check can tell whether
it actually works. These **fixtures** are deliberately prepared examples for
checking those foundations repeatedly, without needing a physical robot.

The **workloads**, meaning the applications FleetForge will manage, use real
ROS 2: the libraries and tools that let robot programs exchange messages.
The programs are **headless**: they need no graphical interface.
They implement the workload part of
[M1-02 (#11)](https://github.com/gleniosp/fleetforge/issues/11).
For the bigger picture, start with the
[release-to-robot walkthrough](../../docs/guides/releases-explained.md).
The [glossary](../../docs/product/glossary.md) provides quick term lookups.

## Why two versions of a counter?

Imagine a robot running version A while we prepare version B. We need to keep
A's software separate, start B with its own dependencies, and distinguish B's
actual behavior from a process that merely claims to be B. These examples let us
exercise those boundaries before the deployment agent is implemented.

[A](../releases/ros-counter-a-v1/release.json) increments a counter by 1;
[B](../releases/ros-counter-b-v1/release.json) increments it by 2. Starting
from zero, two requests produce 1 then 2 for A, and 2 then 4 for B. This small,
observable difference makes it possible to check the application through ROS
messages rather than trusting its version label.

Each version has a **health probe**, a small program that asks the running
application to demonstrate its behavior. Each check sends a fresh unpredictable
challenge, called a **nonce**, which must come back in the application's ROS
reply. The probe also checks which release and running process answered. An old
response, an inactive application or a neighboring workload cannot establish
that the intended new process is healthy.

The demonstration checks successful A/B behavior and deliberately wrong cases.
It establishes the environment and health foundations needed by later deployment
and recovery work. The [experiment report](../../docs/experiments/0002-ros-workload-runtime.md)
records the tested versions, observations and limits. These examples are
**unsigned**: they have no publisher signature proving approval, and are not
trusted deployment inputs.

## What each release contains

A **release** collects one fixed version of the application and the inputs
needed to prepare its **runtime environment**, the installed packages needed
to run it:

- `app/` contains the application and its health probe.
- `pixi.toml` declares its runtime dependencies; `pixi.lock` records the resolved
  packages so installation can use that selection again.
- `release.json`, the **descriptor**, lists its files, their fingerprints, the
  starting command and the expected health behavior.

The release ID names that version. Its descriptor digest is a fingerprint of
its complete definition; the [walkthrough explains hashing](../../docs/guides/releases-explained.md#check-whether-files-changed-fingerprints-and-hashing).
A and B have independently owned manifests, locks and installed environments.
A's inputs stay available alongside B for later recovery/rollback work.

These are real ROS 2 nodes in a minimal FleetForge release layout, with Python
scripts executed directly from Pixi environments. They are not conventional
`ament_python` packages with `package.xml` and `ros2 run` entrypoints. This keeps
the initial runtime/health experiment small; a conventional ROS package can also
be included in a FleetForge release.

## Run the bounded demonstration

Choose where to run the demonstration's scripts and ROS processes:

| Path   | Where it runs                            | Host requirements                                            |
| ------ | ---------------------------------------- | ------------------------------------------------------------ |
| Direct | On Linux, using host Bash and Pixi       | Linux x86_64, Bash, CA certificates and Pixi 0.83.0 or newer |
| Docker | Inside the pinned Ubuntu 24.04 container | Docker capable of running `linux/amd64` containers           |

Both paths install the ROS packages from the release locks into separate Pixi
environments. The Docker image provides Bash, CA certificates and Pixi 0.83.0,
so Docker is the only tool to install for that path.

### Run directly on Linux

On the Linux host, run from the repository root:

```sh
bash examples/ros-workloads/run-demo.sh
```

If the root device environment is already set up, this task invokes the same
script:

```sh
pixi run --locked -e device ros-workloads-test
```

### Run in Docker

Use Docker Engine on Linux, or Docker Desktop on macOS or Windows with Linux
containers enabled. These fixtures target `linux/amd64`; ARM hosts need amd64
emulation, which Docker Desktop provides and which can run more slowly. See
[Docker's platform guidance](https://docs.docker.com/build/building/multi-platform/).

From the repository root, build the reference image and run it. In Bash or zsh
(Linux or macOS):

```sh
docker build --platform linux/amd64 --tag fleetforge-ros-evidence:issue-11 examples/ros-workloads
docker run --rm --platform linux/amd64 \
  --mount type=bind,src="$PWD",dst=/source,readonly \
  fleetforge-ros-evidence:issue-11
```

In PowerShell (Windows):

```powershell
docker build --platform linux/amd64 --tag fleetforge-ros-evidence:issue-11 examples/ros-workloads
docker run --rm --platform linux/amd64 --mount "type=bind,src=$($PWD.Path),dst=/source,readonly" fleetforge-ros-evidence:issue-11
```

The image copies Pixi from its
[official container image](https://pixi.prefix.dev/latest/deployment/container/),
pinned by version and digest in the Dockerfile. Only the repository is mounted
from the host, read-only. The container uses its own Pixi executable and package
cache. Docker requires daemon access; the container uses no privileged mode,
public ports, host networking or hardware access.

The reference run was verified on Linux x86_64. macOS, Windows and amd64
emulation have not been verified for this demo.

The direct path needs package repository access unless the host Pixi cache is
populated. The Docker image build needs apt access; each container run installs
fresh temporary Pixi environments and downloads about 131 MB of compressed
packages because no cache is mounted. Temporary outputs are removed on exit,
and source releases remain unchanged. The
[compatibility evidence](../../docs/experiments/0002-ros-workload-runtime.md)
records the exact package set and platform limits.

The scripts have different jobs:

| Script               | Role                                                                                                     |
| -------------------- | -------------------------------------------------------------------------------------------------------- |
| `run-demo.sh`        | Creates disposable A/B copies, installs their locked environments, then runs ROS checks using A's Python |
| `check_workloads.py` | Starts the ROS applications, runs health and failure checks, and stops/reaps its child processes         |
| `lifecycle.py`       | Requests activation/deactivation through the real ROS lifecycle service for the inactive-node check      |
| `test_helpers.py`    | Pytest regressions for wire parsing, process cleanup and startup deadlines                               |
| `test_ros.py`        | Runs the real ROS verification through pytest in disposable runtime copies                               |
| `test_identity.py`   | Pytest cases for valid, missing and invalid A/B identity context                                         |

Each copy owns a separate `.pixi/envs/default`; source releases and locks stay
unchanged.

Run the portable regressions with `pixi run --locked -e host test` and the
Ruff/mypy checks with `pixi run --locked -e host python-check`. These use root
contributor tools without installing ROS; the direct demonstration continues
to use only the releases' runtime dependencies. The
[development guide](../../docs/guides/development.md#python-tooling-and-workload-tests)
owns Python tool configuration and the immutable formatting boundary.

## Workload and probe interface

The interface that a future supervisor will use follows the
[release specification](../../docs/specs/releases.md#entrypoint-and-ros-health).
The demonstration supplies a fresh random **process-instance ID** for each new
application process. It assigns each instance a separate **ROS domain**, which
separates ROS discovery/communication groups, and private endpoint names.

The counter is a managed ROS node with a **lifecycle**, including inactive and
active states. Its namespace, `/fleetforge/i_<process_instance_id>`, groups
`challenge` and `reply` topics (named message channels) and the
`counter/get_state` service used to ask for its current lifecycle state.

While active, the workload increments its counter for each new `(nonce, sample)`
challenge. Its JSON reply carries the counter value, lifecycle label, nonce,
sample and release/digest/instance identity in a `std_msgs/String` ROS message.
It caches responses for the last 64 nonces so retries do not change a sample,
and stops responding at the signed 64-bit counter limit. No custom message
build, desktop or colcon workspace is needed.

Wire messages are flat JSON objects limited to 4 KiB of UTF-8. The parser
rejects duplicate fields, nested values, invalid Unicode and nonstandard
`NaN`/`Infinity` constants. Invalid challenges produce no reply; malformed
replies make the probe fail.

The probe checks the actual lifecycle service is active, then requests samples
0 and 1 using its nonce. It checks both replies against the expected identity
and verifies that their counter difference is 1 or 2 for the corresponding
release. Success emits the specification's health JSON object, with
`observed_behavior` derived from that measured difference. The internal
monotonic deadline is four seconds; the descriptor/demonstration enforces a five
second process deadline. Probes run serially per instance.

To start each process, `check_workloads.py` obtains **environment activation**
variables with `pixi shell-hook --locked --json`; these tell Python and ROS where
to find the installed packages. It then directly starts the descriptor's
executable in its declared working directory. It discards inherited variables
that could redirect Python/ROS to other installations, disables user-site imports
and bytecode writes, and keeps logs and ROS state in the disposable directory.

The checks cover independent installed environments, release file fingerprints,
A/B behavior/identity, wrong endpoint/domain, deliberately misrouted neighbor,
live inactive lifecycle, stopped workload, stale attempt after restart, and a
child with the wrong counter algorithm despite matching identity. They also
check source inputs remain byte-for-byte unchanged. Real entrypoint failure
checks reject invalid process identity, health nonce and descriptor digest
with nonzero exit and no success output. Deployment startup scheduling,
ongoing supervision and privilege isolation belong to later slices.

The demonstration's lifecycle-control helper shares one deadline across service
discovery and the transition response, using the descriptor's startup budget
(30 seconds here). Its parent allows five additional seconds for Python/ROS
startup and cleanup. Cold discovery may take more than two seconds; an unavailable
service still fails within the configured deadline.

## Runtime dependencies and upgrades

Release manifests target only `linux-64`. A **direct dependency** is a package
the application declares that it needs. Each has a present runtime role:

| Package                    | What the example uses it for                     |
| -------------------------- | ------------------------------------------------ |
| Python                     | Executes the application and probe               |
| `ros-jazzy-rclpy`          | Supplies the ROS node, lifecycle and client APIs |
| `ros-jazzy-std-msgs`       | Supplies the challenge/reply message type        |
| `ros-jazzy-lifecycle-msgs` | Supplies lifecycle service/state types           |

A **transitive dependency** is a package brought in because another dependency
needs it. Python and lifecycle_msgs are also required by rclpy; explicit pins
make these application-facing requirements visible. The locks select matching
Jazzy builds. Both currently contain identical package sets but have independent
ownership, with no shared solve group or writable environment.

No build/development dependency is directly added. Upstream runtime package
requirements also bring in generators, CMake and test/lint packages. The
[upstream handoff](../../docs/experiments/0002-ros-workload-runtime.md#transitive-tooling-handoff)
records that dependency chain and the condition for reviewing it again. We keep
the declared dependencies intact rather than stripping packages after installation.

Once these fixture IDs are accepted, changing code, locks, execution policy or
any descriptor field needs a new release ID and regenerated canonical hashes.
Keep A's original inputs available rather than replacing them with B.

## Dependency review

**Provenance** means where software came from. Each release's lockfile records
the resolved package identities, archive URLs, hashes and declared licenses.
The
[delivery review](../../docs/journal/2026-10-26-ros-workloads.md#dependency-provenance-review)
records the upstream metadata and license-text checks performed for these
fixtures, including their limits. Review dependency changes under the
[third-party policy](../../THIRD_PARTY.md#dependencies-and-tools).

A delivery that distributes packaged environments must collect its inventory
and required license texts and notices from the actual distribution inputs.

## Trust and later lifecycle work

The descriptors reserve `unsigned-demo-publisher` as an illustrative signing
key ID. There is no signature file or trusted publisher binding. The
demonstration checks local file fingerprints for accidental input changes;
The [host release tools](../../docs/guides/release-provisioning.md) provide
checking, provisioning and signing of disposable copies before deployment work. Fresh offline installation, retained
dependency bytes and recovery remain separate deliveries.
