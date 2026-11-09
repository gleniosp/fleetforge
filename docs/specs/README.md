# Specifications

Specifications define formats and behavior shared by implementations.

1. [Immutable releases and local catalog, version 1](releases.md) — Descriptor bytes, publisher signatures, catalog, input limits and ROS health interface.
2. [Agent identity and configuration](agent.md) — Typed IDs, provisioning, startup and liveness.
3. [Agent identity storage](agent-storage.md) — SQLite schema, startup ownership and recovery.
4. [Agent artifacts and activation](agent-releases.md) — independent artifact signatures, compatibility and activation authorization.

The [release examples](../../examples/releases/README.md) include runnable A/B inputs
and [conformance fixtures](../../examples/releases/conformance/v1/README.md)
with fixed expected answers for publisher and agent tests.
Machine-readable contracts live in [schemas](../../schemas/README.md).

[Documentation map](../README.md)
