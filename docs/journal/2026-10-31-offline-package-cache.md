# Offline package cache delivery

M1-05 (#14) adds a Docker Compose fixture proving fresh offline installation from
signed A/B inputs and clear missing-cache failure. A dedicated image copies only
required files; generated state stays in a disposable volume. The
[experiment report](../experiments/0003-offline-package-cache.md) records setup,
commands, results and limits. Source: working tree based on
`182fc67dbbc9dc6705085031822bdc69daf22a5c`.

A parallel Linux x86_64 PR job runs the same fixture, prints preparation logs,
always cleans up, and contributes to the required Repository checks result.
The updated workflow has not yet run on GitHub.

Validation passed locally: Compose configuration, complete offline/ROS regression,
cleanup, image input inspection, `pixi run --locked -e host format`,
`pixi run --locked -e host check` and `git diff --check`. The complete diff was
manually reviewed. Docker Desktop/emulation and full deployment recovery remain
unverified. Changes are uncommitted for maintainer review.
