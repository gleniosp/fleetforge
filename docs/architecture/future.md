# Deferred platform architecture

**Status:** Accepted evolution constraints, deferred implementation. Activate
work explicitly through the [roadmap](../roadmap.md#future-platform) and its
issue gates. The
[requirements](../product/requirements.md#future-capability-boundaries) own
scope; this document owns future architectural constraints and required
evidence.

## FUT-01 — Peer reachability

Extend the planned MVP secure direct protocol with authenticated
discovery/membership, justified alternate transports, NAT traversal and optional
relays. Membership and relay access grant no deployment authority. Evaluate real
reachability and abuse boundaries before choosing topology. Test unauthorized
discovery, NAT/relay loss, resource bounds and local execution independence.
MQTT remains a justified optional broker integration; QUIC is a future choice,
not a replacement already selected.

## FUT-02 — Distributed synchronization

Share selected signed/authorized state with durable replication and bounded
anti-entropy. Define conflicts per data type before choosing algorithms; do not
introduce speculative CRDTs or automatic multi-writer execution.
Assignment/authority transfer requires device-side fencing/confirmation.
Unreachable transfers stay pending. Test partitions, stale writers, replay and
convergence without merging execution authority or disclosing another tenant's
state.

## FUT-03 — Artifact delivery and caches

Provide authorized content-addressed delivery, resumable P2P transfer and
peer/edge cache policy. Hash possession grants no download access. Protect
active and known-good inputs from eviction; edge outage cannot make local
execution/recovery dependent on a cache service. Validate authorization,
corruption, interruption, resume, quota/eviction and offline recovery with real
bytes before claiming delivery.

Specify how a complete verified release becomes locally available through a
protected catalog update, including interruption and conflicting ID/digest
bindings. This enables remote provisioning of new releases while the current
workload continues running; the MVP assumes trusted pre-provisioning instead.

## FUT-04 — Advanced rollouts

Add canaries/waves, fresh-health gates, scheduling, durable admissions,
concurrency, pause/resume and rollout UI. An uncertain disconnected activation
holds reserved concurrency until confirmed terminal or fenced; token expiry
alone cannot release strict capacity. Pause blocks new admissions and cannot
instantly cancel offline transitions. Test lost contact, stale health, restart,
fairness and paused admission against actual device outcomes and explicit
capacity accounting.

## FUT-05 — Advanced robotics

Extend the MVP's real ROS 2 slice with selected Gazebo physics, advanced
workloads, hardware drivers/navigation and bounded physical pilots. Validate
reproducible simulation first. Physical work requires approved security,
device-platform and safety prerequisites plus explicit authorization. No
physical safety claim follows from deployment health or simulation; pilot
evidence stays bounded to tested hardware.

## FUT-06 — Production security

Harden enrollment and credential lifecycle, protected publisher signing and
metadata trust lifecycle, incident runbooks and independent security review. MVP
already requires peer/operator authentication, authorization, signed
instructions/releases and privilege boundaries. Test revocation/rotation, key
compromise, recovery and trust-root changes; TUF-style lifecycle is a future
design gate. Shared untrusted production use requires this evidence, not merely
a trusted-local demonstration.

## FUT-07 — Optional observability services

Export bounded OTel/log/metric/trace data to retained storage, dashboards and
alerts. Control cardinality, privacy, quotas, tenant scope and retention.
Collector failure must never become an execution dependency. Test exporter
backpressure/loss, telemetry isolation, historical freshness and alert/runbook
behavior; operational MVP events remain useful without a centralized telemetry
platform.

## FUT-08 — Production device platforms

Prioritize Linux ARM64 (`linux-aarch64`) as the first device-platform expansion,
before other architectures or operating systems.
Validate an explicit native/ARM64 platform matrix, installation, boot
supervision, agent/schema upgrades and recovery. Preserve identity and accepted
intent. Never blindly roll back a binary across an incompatible schema. Test
interrupted upgrades, boot failures, compatibility and resource budgets on
selected real platforms before claiming support beyond the Linux x86_64
reference container.

## FUT-09 — Tenancy

Extend existing identity/ownership/assignment context with organizations, roles,
delegation and quotas. Enforce isolation at API, job, database, protocol,
artifact, log and cache boundaries. Ownership transfer revokes old access and
preserves original historical context without exposing another tenant's history.
Test adversarial cross-tenant access, noisy neighbors and fenced transfer;
single-tenant MVP schema preparation is not evidence of production
multi-tenancy.

## FUT-10 — Optional central management

An optional central API/PostgreSQL may own inventory, administrative intent,
jobs, history and current projections. Its first migration is tenant-aware, with
tenant-scoped composite constraints/indexes and row-level security using
application roles that are neither table owners nor `BYPASSRLS`. Test isolation
using the actual application role, including jobs and restore paths.

Define whether the logical deployment authority is local or hosted. Gateways do
not automatically become authority; hosted authority needs WAN for new intent,
while accepted work executes/restarts/recovers locally. Device SQLite retains
local execution/recovery truth. Rebuild projections without replaying commands;
stale backups with lost authority request ledgers quarantine ambiguous state
rather than raising counters and replaying old intent. Test placement, offline
behavior, projection rebuild, restore ambiguity and historical privacy.

## FUT-11 — Cloud infrastructure and IaC

Evaluate providers/IaC against concrete authorized service needs. Deliver
focused isolated environments/networking/state, managed resources, delivery
pipelines, secrets/teardown and backup/restore drills. No paid provisioning
without explicit task authorization. Require reproducible change/recovery
evidence and resource/cost ownership before calling an environment operational.

## FUT-12 — Hosted architecture and measured scale

Decouple management API, jobs, persistent connection gateways, bounded
high-volume ingestion and blobs. PostgreSQL owns metadata, intent, jobs and
current projections; use pooled database access, never a connection per device.
Object/cache storage owns large blobs. If a broker crosses a durable boundary,
add a transactional outbox rather than relying on an atomic
database-plus-publish operation.

Tenant placement maps to regions/cells independently of IDs; large tenants can
span partitions. There is no mandatory site gateway or global all-to-all mesh.
Validate placement, shared-service capacity, failure isolation, disaster
recovery and cost against concrete service needs before selecting production
runtimes.

Every scale claim declares assets, devices per asset, concurrent TLS sessions,
reconnect rate, events/s, bytes/s, readers, artifact egress, per-tenant
fairness, memory/disk and p95/p99 budgets. Millions of assets/devices are a
future measured target. Three real agents and bounded synthetic-peer tests
establish MVP correctness and resource behavior, not production capacity.
Prioritize hardened device operations and peer reachability/artifact delivery
after MVP; SaaS remains optional.
