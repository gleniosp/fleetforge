# Optional connectivity and messaging evaluation

**Status:** Evaluation criteria, not a protocol migration. The
[MVP coordination contract](coordination.md#selected-transport) selects direct
device-initiated mutual-TLS WebSocket. [#49](https://github.com/gleniosp/fleetforge/issues/49),
[#66](https://github.com/gleniosp/fleetforge/issues/66) and
[#82](https://github.com/gleniosp/fleetforge/issues/82) own future evidence.

| Domain                                 | Current or candidate transport                                                 | Required invariant and evaluation                                                                                                                    |
| -------------------------------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Authority → robot control              | MVP direct WebSocket; later persistent gateway or evaluated MQTT               | Signed, scoped, monotonic intent; durable acceptance, stale-command rejection and local recovery are application rules, not transport QoS            |
| Robot → platform observations          | MVP same session with bounded cursor catch-up; optional telemetry exporter     | Preserve source time, gap and backpressure; keep operational status distinct from training data                                                      |
| Robot ↔ robot and site synchronization | Discovery/relay/Zenoh or other P2P candidate                                   | Membership gives no authority; authenticate peers, fence writers, authorize each data class and test partitions                                      |
| Backend domain events and jobs         | Proposed PostgreSQL outbox plus evaluated EventBridge/SQS or self-hosted queue | At-least-once consumers need deduplication, bounded retries/dead letters and replay policy; do not publish as if a DB transaction covered the broker |
| Artifact and dataset bytes             | Authorized HTTPS/object transfer, peer/edge cache where justified              | Verify complete immutable digest and grants after resume; do not put recordings into control messages                                                |
| Robot-internal application traffic     | ROS 2/DDS inside the workload boundary                                         | Application topology never grants FleetForge deployment authority                                                                                    |

Evaluate WebSocket, MQTT, NATS JetStream, Zenoh, HTTPS/gRPC and relevant P2P
transports against the particular domain, including ordering, delivery,
reconnection, offline storage, fan-out, backpressure, latency, authentication,
tenant isolation, operating cost and portability. A transport-neutral _domain_
contract is useful for signed intent and durable state; a generic transport
framework without a second implementation is premature.

MQTT may suit brokered device connectivity or small telemetry, but its topic ACLs,
session behavior and QoS do not prove one-time deployment execution. NATS
JetStream may suit selected backend/site events; Zenoh may suit robotics data
exchange. They solve different candidate problems and need separate bounded
fixtures. Kafka or another stream platform needs measured retention/throughput
requirements. NAT traversal requires authenticated rendezvous/relay, scoped
grants, rate limits and relay-loss tests. A connected peer may still be stale,
compromised or unauthorized.

Future decisions should compare AWS IoT Core, API Gateway WebSocket, a persistent
gateway behind a load balancer and a self-hosted gateway using current provider
limits, protocol compatibility and reconnect cost. The [hosted reference](platform-evolution.md#hosted-reference-alternatives-and-decision-gates)
records placement boundaries. No device gateway or public internet is required
for the MVP.
