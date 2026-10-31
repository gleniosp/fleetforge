# Check the locked contributor toolchain in a container

This optional fixture checks the current Pixi/Cargo toolchain in disposable
Ubuntu 24.04 userspace. It verifies isolated executable paths, builds and lints,
rejects lockfile drift and unsafe Rust, and checks that source inputs stay intact.
It is separate from the normal contributor tasks and runs only on Linux x86_64
containers; other hosts need Docker's amd64 emulation, which is unverified here.

From the repository root, with Docker and Compose installed:

```sh
docker compose -f experiments/pixi-toolchain/compose.yaml run --build --rm verify
```

The image contains pinned Pixi and only the source/configuration files required
by `verify.sh`. It mounts no host checkout, executable or cache. The script runs
inside the container, copies named inputs into a fresh workspace, and removes
that workspace on exit. Installing the locked environments and formatter plugin
requires internet access and disk space for the toolchains.

The command returns nonzero if a check fails. The container and its generated
state are removed on exit; console output provides the results. Clean up the
Compose network when finished:

```sh
docker compose -f experiments/pixi-toolchain/compose.yaml down
```

The [validation report](../../docs/experiments/0001-pixi-toolchain.md) records
the current tested versions, inputs, results and limits.
