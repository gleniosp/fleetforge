# Optional robotics data and model lifecycle

**Status:** Future requirements for review. Operational status in the MVP remains
the [bounded observation contract](coordination.md#bounded-synchronization-and-freshness).
No data platform or training service is a prerequisite for local deployment.

Three data classes need different consent, retention and failure behavior:
operational telemetry explains current/last-known robot state; diagnostic
recordings support bounded troubleshooting; curated datasets may be used for
training. A telemetry exporter must not silently convert all sensor output into
a training dataset. Capture is explicitly scoped by tenant, asset, topic,
purpose, time, privacy and budget. Local buffering needs finite storage and a
drop/retention policy that protects execution and recovery space.

The optional flow is capture → validate/label → resumable authorized upload →
immutable dataset registration → lineage and access review → training/evaluation
job integration → model candidate → independent release approval → signed model
artifact → ordinary authorized deployment → inference observation. A training
service can propose a candidate; it cannot sign as publisher, approve promotion
or allocate device generations. Device-produced variants require producer/parent
lineage and quarantine before synchronization or promotion.

ROS 2 topic capture with rosbag2/MCAP is an evaluation candidate, not a chosen
recording format. Large recordings belong in protected object storage or
resumable transfer with digest checks, not MQTT control payloads. Dataset
metadata should retain source identity, capture policy, schema/version,
license/consent, transformations, integrity, retention and deletion lineage.
Access must be tenant-scoped through upload, catalog, training job and output.

Training integration should begin with one externally produced model candidate
and a reproducible evaluation corpus, not a FleetForge-owned training platform.
Compare external job handoff with a self-hosted worker only when workload,
privacy and cost needs exist. Quality evidence must name dataset version,
method, metrics and supported target. No measured inference quality implies
robot physical safety. [#160](https://github.com/gleniosp/fleetforge/issues/160)
owns model schema/compatibility, [#161](https://github.com/gleniosp/fleetforge/issues/161)
the first offline inference fixture, and [#162](https://github.com/gleniosp/fleetforge/issues/162)
through [#164](https://github.com/gleniosp/fleetforge/issues/164) bounded
distribution/local-variant/optimization research.

The new [DATA and ML requirements](../product/requirements.md#optional-data-model-and-commercial-requirements)
require consent/privacy failures, interrupted upload, wrong-tenant access,
lineage conflict, poisoned/unknown input, incompatible target and failed
inference/recovery tests. Dataset retention and training outputs need explicit
owners and deletion semantics; an offline device cannot promise immediate
revocation or deletion.
