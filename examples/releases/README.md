# Release examples

These examples support development and verification of the release lifecycle.

| Directory                                  | Purpose                                                                  |
| ------------------------------------------ | ------------------------------------------------------------------------ |
| [ros-counter-a-v1](ros-counter-a-v1/)      | Runnable locked ROS workload: counter increments by one                  |
| [ros-counter-b-v1](ros-counter-b-v1/)      | Runnable locked ROS workload: counter increments by two                  |
| [conformance/v1](conformance/v1/README.md) | Shared test fixtures with fixed answers for the version 1 release format |

The A/B directories contain immutable descriptors, payloads and runtime locks.
Their committed inputs have no signatures. Follow the
[signing and provisioning guide](../../docs/guides/release-provisioning.md) to
sign disposable copies and verify publisher approval, or the
[ROS demonstration](../ros-workloads/README.md) to run their behavior checks.
The conformance fixtures use illustrative placeholder payloads and cannot be installed.

Moving an example does not change its release ID or descriptor digest. Changes
to its payload, descriptor or signing key binding require a new release ID under
the [release contract](../../docs/specs/releases.md#documents-and-identity).
