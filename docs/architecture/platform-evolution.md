# Optional hosted platform and portability

**Status:** Future design for review, not an implemented or activated service.
The [MVP topology](overview.md) and [offline authority rules](coordination.md)
remain the operative contracts. [#169](https://github.com/gleniosp/fleetforge/issues/169)
owns this documentation review; [FUT-10](future.md#fut-10--optional-central-management)
through [FUT-12](future.md#fut-12--hosted-architecture-and-measured-scale)
own later delivery.

## Local-first boundary

Robot execution, accepted intent, health checks and recovery remain local. An
optional hosted control plane may coordinate new desired outcomes, inventory and
history; losing it may delay new instructions but must not undo accepted local
work. A peer or gateway can carry bytes or observations without becoming the
deployment authority. Authority transfer requires device-side fencing and leaves
unreachable transfers pending. Offline revocation cannot be instantaneous.

These choices trade immediate global control for continued local operation and
require explicit stale observation, conflict and credential-expiry handling.
[FUT-01](future.md#fut-01--peer-reachability) and
[FUT-02](future.md#fut-02--distributed-synchronization) evaluate peer reachability
and selected-state synchronization separately. The [coordination contract](coordination.md)
owns the exact command semantics.

## Logical planes and data ownership

| Plane           | Responsibility                                                                                      | Durable truth and failure boundary                                                                                                                 |
| --------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Robot execution | Verify accepted instructions and artifacts; install, supervise, observe and recover workloads       | Device SQLite, protected local inputs and actual processes; independent of hosted availability                                                     |
| Control         | Authorize deployment intent, registry/assignment, request ledger, inventory and current projections | Local authority for MVP; optional hosted placement needs an explicit ownership decision in [#74](https://github.com/gleniosp/fleetforge/issues/74) |
| Data            | Optional telemetry, recordings, dataset registration and model evaluation evidence                  | Separate retention and authorization from command state; collector failure cannot block execution                                                  |

Logical planes do not imply three services. Start future hosted work with the
fewest deployable units that satisfy measured isolation and scaling needs.
PostgreSQL is the proposed transactional store for hosted metadata, intent and
jobs; device SQLite remains local truth. Use tenant-aware constraints and actual
application-role isolation from the first hosted migration. Large immutable
blobs belong in protected object storage, while database records bind identity,
digest, authorization and retention. Pool database access; a device connection
must not require its own database connection. [#75](https://github.com/gleniosp/fleetforge/issues/75)
and [#82](https://github.com/gleniosp/fleetforge/issues/82) validate these choices.

## Hosted reference, alternatives and decision gates

AWS is the preferred **reference candidate** for an initial hosted deployment;
it is not a required FleetForge runtime. The provider and IaC choice remains
open in [#79](https://github.com/gleniosp/fleetforge/issues/79). A self-hosted
reference must eventually demonstrate the application guarantees without
pretending that cloud-specific service behavior is portable.

| Concern                  | Candidate and reason to evaluate                                                                      | Alternative and trade-off                                                                                                                     | Decision owner                                                                                                     |
| ------------------------ | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Operator API and console | HTTP API behind managed TLS/load balancing; ordinary request/response suits bounded reads and writes  | Self-hosted reverse proxy reduces provider dependency but adds operations                                                                     | [#74](https://github.com/gleniosp/fleetforge/issues/74), [#82](https://github.com/gleniosp/fleetforge/issues/82)   |
| Device sessions          | Persistent gateway on a suitable managed container/VM runtime can preserve the MVP WebSocket protocol | API Gateway WebSocket and AWS IoT Core need protocol, mTLS, lifecycle, quota and cost evaluation before adoption; no gateway grants authority | [#82](https://github.com/gleniosp/fleetforge/issues/82), [#83](https://github.com/gleniosp/fleetforge/issues/83)   |
| Transactional state      | Managed PostgreSQL can retain the proposed domain model and operations support                        | Self-hosted PostgreSQL offers on-premises operation with a larger backup/patching duty                                                        | [#75](https://github.com/gleniosp/fleetforge/issues/75), [#110](https://github.com/gleniosp/fleetforge/issues/110) |
| Blob storage             | S3 is an AWS reference candidate for immutable artifacts and optional datasets                        | S3-compatible/on-premises storage needs tested integrity, access and retention semantics; filesystem is useful locally                        | [#51](https://github.com/gleniosp/fleetforge/issues/51), [#110](https://github.com/gleniosp/fleetforge/issues/110) |
| Infrastructure           | OpenTofu is the preferred open-source evaluation candidate                                            | Terraform, Pulumi and provider CDKs differ in governance, language, state and migration burden                                                | [#79](https://github.com/gleniosp/fleetforge/issues/79)                                                            |

API Gateway WebSocket currently documents a two-hour maximum connection and
ten-minute idle timeout. That is a reason to test reconnect behavior, not a
selection of API Gateway for FleetForge. Recheck [AWS's live quotas](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-execution-service-websocket-limits-table.html)
when #82 runs. Service choice must show device identity and authorization,
protocol compatibility, bounded reconnect load, connection cost and failure
recovery with actual measurements.

## Portability and automation

Keep domain rules for signed intent, release identity, reconciliation and
tenant authorization above provider interfaces. Add an adapter only when two
real implementations or a concrete boundary need it. Storage streaming,
integrity checks and authorization can have a common contract; queue ordering,
delivery, retries and retention must expose provider differences. A generic
database-provider wrapper is not a prerequisite for PostgreSQL.

For future asynchronous jobs, a transactional outbox with idempotent consumers
is a **proposed** way to avoid assuming an atomic database-plus-broker commit.
AWS EventBridge/SQS and a self-hosted queue are candidates; NATS JetStream and
other brokers need workload evidence. [Connectivity and messaging](connectivity-and-messaging.md)
owns the comparison. No backend broker is needed for the MVP.

Platform CI/CD, workload release CI/CD and Agent/OS updates have separate
approval and rollback paths. Platform CI validates IaC, previews changes,
promotes reviewed service artifacts, applies approved migrations and verifies
restore. Workload CI builds/tests the ROS application, records provenance,
signs immutable release inputs, publishes package bytes, then separately
registers/promotes a release; deployment remains an authorized intent.
Bootstrap/Agent and OS recovery follow their independent owners in
[agent delivery](agent-delivery.md). [#111](https://github.com/gleniosp/fleetforge/issues/111)
owns service deployment automation; [#158](https://github.com/gleniosp/fleetforge/issues/158)
owns release provenance.

Capacity and availability targets are unresolved. #82 must declare device and
session counts, reconnect rate, event/byte throughput, readers, artifact egress,
tenant fairness, resource budgets, p95/p99 latency, availability, RTO/RPO and
cost before choosing a production runtime. [#84](https://github.com/gleniosp/fleetforge/issues/84)
and [#113](https://github.com/gleniosp/fleetforge/issues/113) must test failure
and placement. No million-device claim follows from the MVP's three agents.
