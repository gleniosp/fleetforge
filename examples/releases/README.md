# Release examples

These examples support development and verification of the release lifecycle.

| Directory                                  | Purpose                                                                  |
| ------------------------------------------ | ------------------------------------------------------------------------ |
| [ros-counter-a-v1](ros-counter-a-v1/)      | Runnable locked ROS workload: counter increments by one                  |
| [ros-counter-b-v1](ros-counter-b-v1/)      | Runnable locked ROS workload: counter increments by two                  |
| [conformance/v1](conformance/v1/README.md) | Shared test fixtures with fixed answers for the version 1 release format |

The A/B directories contain descriptors, application payloads and runtime locks.
Their committed inputs have no signatures. Follow the
[signing and provisioning guide](../../docs/guides/release-provisioning.md) to
sign disposable copies and verify publisher approval, or the
[ROS demonstration](../ros-workloads/README.md) to run their behavior checks.
The conformance fixtures use illustrative placeholder payloads and cannot be installed.

The A/B v1 examples use `demo-publisher-1` as their local publisher key ID.
The maintainer revised this development baseline in place while these inputs
serve only as examples. Their descriptor digests changed; recreate any catalogs
and signing fixtures made from the earlier descriptors. Workload files, runtime
manifests and locks retain their original bytes.

For published releases and retained deployment/recovery inputs, follow the
[immutable release contract](../../docs/specs/releases.md#documents-and-identity):
a changed descriptor requires a new release ID. The development-example revision
is recorded in the [publisher trust journal](../../docs/journal/2026-10-31-publisher-trust.md#demo-publisher-identity).
