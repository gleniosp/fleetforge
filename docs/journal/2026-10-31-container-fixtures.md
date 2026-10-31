# Container fixture inputs and launchers

Working tree based on `97f88ce2a7e57090ff27501abf965079382442c2`.
The ROS demo and toolchain images now copy explicitly selected inputs and run
without host mounts. Both have Compose launchers; host Bash and Pixi are
unnecessary for these paths. Container scripts remain available for their
installation and verification logic.

`run-demo.sh` and `verify.sh` copy named files into fresh temporary workspaces,
reject symlinks and non-regular file inputs and clean up on exit. The toolchain verifier now
accepts Python in the default environment, matching the current manifest, while
still rejecting contributor-only tools there. Its image includes pinned Pixi.

Validation passed on Linux x86_64:

- Both documented Compose build/run commands, including real ROS behavior and
  toolchain builds, lock-drift rejection, unsafe-Rust rejection and source preservation.
- Container fault checks replacing a selected input with a symlink or FIFO: both scripts
  rejected it before invoking Pixi.
- Compose configuration, shell syntax, image input inspection and cleanup.
- Host portable tests: 105 passed; device tests: 10 CLI tests and one real ROS test passed.
- Repository `format`, host `check`, device `device-check` and `git diff --check`.

[ROS usage](../../examples/ros-workloads/README.md#run-in-docker) and
[toolchain usage](../../experiments/pixi-toolchain/README.md) explain reproduction.
Docker Desktop and amd64 emulation remain unverified. Changes are uncommitted
for maintainer review. The toolchain experiment report contains the current rerun
results.
