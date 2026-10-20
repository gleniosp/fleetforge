# Product requirements

**Status:** Accepted product direction; implementation and verification are
delivered through the linked GitHub work. This file defines the contract, not
current software capabilities.

## Vision and operating model

FleetForge is a local-first, Pixi-native robot software lifecycle platform. A
logical Rust/Tokio authority persists desired software; a Rust/Tokio agent on
each device owns accepted execution, health, and recovery. A
SvelteKit/TypeScript console presents the authority's observations. Cloud
hosting, a central server, a broker, and a per-site gateway are optional future
deployment choices.

Accepted work continues during authority loss when trusted release inputs and
resources are local. Public internet loss alone does not prevent new deployments
from a reachable local authority. These are distinct failure cases.

There are three scopes:

1. **Bootstrap:** reproducible engineering tooling and documentation. It is not
   the functional MVP.
2. **Functional MVP:** a real deployment lifecycle across three simulated robots,
   one operator, and a functional console.
3. **Future platform:** capability expansions with separate decision gates.

## Domain terminology

| Term | Meaning |
| --- | --- |
| Asset | Maintainable robot identified by `asset_id` |
| Device | Managed computer/endpoint identified by `device_id`, distinct from an asset or agent process |
| Tenant | Owning organization/context identified separately by `tenant_id` |
| Assignment | Binding of asset, device, tenant and logical deployment authority, identified by `assignment_id` |
| Authority | Single deployment writer for an assignment, identified by `authority_id`; operator denotes its local service/UI role |
| Fleet | Configured selection of assets/devices, independent of network addresses |
| Release | Immutable publisher-signed descriptor and its application, Pixi manifest and lockfile inputs |
| Release catalog | Mapping from supported release IDs to immutable descriptors/digests |
| Desired state | Authorized target release and descriptor digest for an assignment/device at a generation |
| Generation | Durable increasing counter scoped to authority/assignment/device |
| Request ID | Identity recognizing retries, separately at API submission and instruction delivery |
| Acceptance | Agent validated and committed an instruction; execution may still be pending |
| Deployment attempt | Correlated effort to satisfy an accepted generation |
| Active release | Software associated with the actual managed workload; absent/unknown are explicit |
| Known-good release | Software that previously passed workload health verification |
| Automatic recovery | Restore and verify known-good software after failed deployment |
| Requested rollback | Issue a new generation targeting a retained previous release |
| Observation | Last received source snapshot with identity, sequence, source time and freshness |
| Durable event | Bounded persisted operational history, separate from stdout and security decision records |

## Fixed MVP boundary

| Concern | Contract |
| --- | --- |
| Ownership | One configured tenant, three assets with one device/agent each; schema permits asset-to-many-devices without orchestration |
| Authority | One local Rust/Tokio authority and private SQLite; manually configured/provisioned peers |
| Agents | Independent Rust/Tokio agents, private SQLite/state/runtime/cache and credentials |
| Software | Small headless ROS 2 Jazzy Python A/B releases, each with independent Pixi manifest/lock/runtime |
| Release availability | Pre-provisioned immutable inputs and all dependency package bytes |
| Device transport | Device-initiated direct WebSocket over TLS 1.3 mutual TLS; bidirectional push |
| Trust | Registry authorization, detached Ed25519 signatures, protected agent/workload OS boundaries |
| Lifecycle | Separate preparation, controlled stop/start, health verification, recovery and explicit rollback |
| Interface | Authenticated local API with bounded stored-projection polling; SvelteKit/TypeScript console |
| Simulation/platform | Docker Compose, Linux x86_64, Ubuntu 24.04 reference container; actual RoboStack/Pixi combination must be validated |
| Visibility | Bounded logs/events, source freshness, desired/accepted/active/outcome and per-device partial results |

The [architecture](../architecture/overview.md) owns identity, trust, protocol
and failure invariants; capability acceptance below does not imply
implementation.

## Functional requirements

### MVP-01 — Engineering foundation

Provide root Pixi and virtual Cargo workspaces, one meaningful Rust executable,
reproducible toolchain/lockfiles, canonical tasks, GitHub Actions, license,
contribution/agent conventions, initial ADRs, and GitHub-linked planning.

Use separate Pixi `dev` and `build` environments with shared toolchain features.
Development includes Pixi-managed prek and Commitizen. Use `prek.toml`, local
pre-commit and commit-msg hooks, and matching CI validation. Introduce Ruff
linting/formatting and mypy with the first Python code; keep them out of
deployed workloads. Rust uses rustfmt and Clippy. Checks must preserve tracked
sources and lockfiles; format/fix are explicitly mutating. Cleaning must
preserve operational state. Add tasks and packages only when they perform
meaningful work.

**Acceptance:** a contributor can clone, install the locked environment, build
and invoke the executable, and reproduce formatting, linting, tests, and CI.
Bootstrap requires no SQLite, peer networking, web app, deployment engine, or
purpose-free infrastructure.

### MVP-02 — Reproducible software releases

Provide independent A/B releases of a small headless ROS 2 Jazzy Python
workload. Each has a stable ID, manifest, lockfile, files, executable
entrypoint, health contract, publisher-signed immutable descriptor, and
integrity information. Authority and devices agree on the explicit catalog.
Unknown, missing, or mismatched releases fail clearly.

**Acceptance:** fresh installed environments execute genuinely different
application behavior, not only different version metadata; health identifies the
running release and process instance through actual ROS
lifecycle/message/service behavior. Isolated ROS domains/fixtures prevent a
neighbor or stale process from satisfying health. Validate real package
compatibility; preserve an actionable reproducer for upstream gaps instead of
silently substituting a generic mock.

### MVP-03 — Durable robot agent

Provide separate strongly typed asset/device identities and
tenant/authority/assignment context from the first schema, configuration, SQLite
migrations, supervised processes, liveness, workload health, structured logs,
and recovery-capable startup. As lifecycle concepts arrive, persist desired
state/generation, attempt, active and known-good release, and recovery metadata.

**Acceptance:** restart preserves identity and critical operational state; the
agent inspects durable state and real process/filesystem evidence before acting.
Identity and ownership follow the [identity
contract](../architecture/identity.md). Corrupt/unreadable storage fails
explicitly. Protect keys, policy, state and trusted inputs from workloads with
separate OS users/permissions and unique credentials.

### MVP-04 — Local deployment lifecycle

Resolve local releases, verify publisher signatures and integrity, prepare Pixi
environments separately, activate real processes, verify workload health, report
success, and recover to known-good software on activation/verification failure.
Failed recovery is an explicit outcome. Retain A for recovery and later rollback
even after B succeeds.

**Acceptance:** deploy B from A; a real failing B health check restores verified
A. Preparation failure preserves healthy A. Failed recovery is observable, and
terminal failed generations do not create endless deploy/recover loops.
Application-data migration reversibility is separate; MVP workloads avoid
incompatible persistent-data migrations.

### MVP-05 — Direct operator communication

A local Rust/Tokio authority and three configured device agents communicate over
mutually authenticated TLS 1.3 WebSocket sessions initiated by devices. Push
desired state and observation transitions; use bounded heartbeats,
reconnect/backoff with jitter, snapshots and cursor-based event catch-up.
Authenticate and authorize peers against identity/assignment bindings and verify
authority-signed instructions.

**Acceptance:** wrong CA, peer, tenant, assignment, authority, key, expired
credential and tampered payload reject before durable acceptance. Reconnect
preserves local work and synchronizes actual state within declared resource
bounds. Transport receipt never proves durable acceptance or deployment success.
Browser traffic uses a separate authenticated API over stored projections.

### MVP-06 — Declarative reconciliation

Persist authority/assignment/device context, desired intent, request IDs, and
increasing generations. Version messages, deduplicate instructions, reject stale
generations and equal-generation conflicts, reconcile after restart, and
synchronize status on reconnect. A newer generation targeting already healthy
active software is satisfied without unnecessary process replacement.

**Acceptance:** retries, duplicates, stale/conflicting messages, lost
acknowledgments, and restarts cause no unintended deployments or generation
reuse. Requested rollback to A is a new generation. Deduplicate immutable
payload semantics, independent of signature or transport representation.
Serialize transitions with safe supersession. Quarantine ambiguous stale
authority restores with a lost request ledger; never raise counters
automatically to replay uncertain old intent.

### MVP-07 — Operational observability

Introduce diagnostics with the operational agent, then extend them with each
capability. Include component/asset/device/tenant/assignment/authority identity,
request/attempt correlation, release, generation, phase, timestamps, meaningful
error codes/messages, and useful durations. Persist significant lifecycle events
with deduplication identifiers.

Expose liveness separately from workload health, desired/accepted/active state,
current progress, last outcome, recovery, last contact, and bounded recent
history. Bound general output handling separately. Report event retention gaps;
do not promise indefinite history or exactly-once event delivery.

**Acceptance:** each demonstrated deployment can be explained from request to
acceptance, execution, failure/success, actual active release, and recovery.
Disconnected status is labelled last observed, never current certainty. Preserve
source time separately from intermediary receipt/contact time; reconnect or DB
reload cannot refresh old health. Bound local security decision records
separately.

### MVP-08 — Independent simulated fleet

Run three agents and one operator in Docker Compose, adding the frontend when
implemented. Give robots separate identity, SQLite, runtime directories, caches,
and relevant mutable release storage. Provision unique credentials and isolated
ROS domains/health fixtures. Configure direct addresses and controlled
network/health/process faults. Normal shutdown preserves persistent state; reset
is separate and explicit.

**Acceptance:** robots demonstrate different outcomes without accidental shared
state, and deterministic scenarios clean up only their own resources.

### MVP-09 — Functional operator console

SvelteKit displays actual Rust operator observations: identity,
contact/freshness, connectivity, liveness, workload health, active/desired
release, generation, progress, recent events, errors, and recovery. Provide
deploy-B, inspection, and rollback-to-A controls for selected/all configured
assets/devices through authenticated, idempotent submissions with
same-origin/CSRF protection. Include bounded event pages and workload log tails
with truncation/gaps. Represent independent per-device outcomes and partial
success accurately.

**Acceptance:** UI controls cause real operator intent and robot execution; the
console reports observed outcomes and stale/unknown state honestly.

### MVP-10 — Constrained offline operation

Test these independently, with verified network conditions and fresh fixtures:

| Scenario | Preconditions/action | Required result |
| --- | --- | --- |
| A: internet unavailable | A healthy; B files/packages local; B environment absent; operator reachable | Fresh locked offline B preparation, execution, and health verification without downloads |
| B: operator lost after acceptance | Prove durable robot acceptance, then disconnect operator | Robot completes or recovers; reconnect synchronizes actual state and available events |
| C: robot lost before delivery | Disconnect robot, then persist new operator intent | Intent stays pending; latest relevant generation is safely delivered on reconnect |
| D: package bytes missing | Fresh environment, incomplete cache, internet blocked | B preparation fails clearly; healthy A remains safe |
| E: agent interrupted | Stop at controlled deployment stages; retain storage | Startup inspects SQLite, filesystem, and processes, then resumes or recovers safely |
| F: operator restarted | Persist intent; interrupt around delivery/acknowledgment | Authority/generations survive, with no lost intent, reuse, or unintended redeployment |

Credential expiry prevents new authorization and terminates or revalidates
existing sessions; accepted local execution continues subject to trusted
inputs/resources. Offline revocation cannot be instantaneous. When authority is
unreachable, no new desired state is invented.

Existing workloads continue without public internet. Agent/container restart may
interrupt the workload during recovery; uninterrupted execution is not promised.
A lockfile identifies dependencies but does not supply their package bytes. An
already installed B environment is not evidence of fresh offline installation.

**Acceptance:** each scenario proves the intended allowed/blocked paths and real
process outcomes rather than relying on configuration flags or database labels.

### MVP-11 — Complete reproducible demonstration

Automate and document seven phases using independent or explicitly reset
fixtures:

1. Start three healthy A workloads, operator, and dashboard; inspect identities,
   liveness, health, logs, and events.
2. Request B fleet-wide: two verified B successes; one deterministic real B health
   failure with verified recovery to A and accurate partial-outcome reporting.
3. Request A for a robot on B as a new generation; verify actual rollback/health.
4. Prepare B fresh from local cache with internet blocked and operator reachable.
5. Accept B durably, disconnect operator, complete/recover locally, then reconnect.
6. Queue intent for an unreachable robot, reconnect, and reconcile safely.
7. Interrupt/restart agent and operator at controlled boundaries; inspect durable
   state, process evidence, diagnostics, and eventual convergence.

Include negative evidence for missing offline dependencies and failed recovery.

**Acceptance:** documented commands reproduce the complete workflow from a clean
development setup with real processes, bounded deterministic checks, and no
dependency on future capabilities.

## Non-functional requirements

| ID | Contract | Verification approach |
| --- | --- | --- |
| NFR-01 | Durably persist accepted intent, identity, generations, and recovery metadata | Migration, abrupt restart, lost-ack, and crash-boundary tests |
| NFR-02 | Protect active/known-good inputs; serialize incompatible activation; bound retries | Preparation/activation/recovery failure and concurrency tests |
| NFR-03 | Reproduce tooling and release environments with owned committed lockfiles | Clean Linux setup, locked validation, fresh runtime installs |
| NFR-04 | Explain meaningful transitions and uncertainty with bounded diagnostics | Event/API/UI assertions, retention and stale-state tests |
| NFR-05 | Bound messages/pages/queues/output/history/timeouts/retries/disk; reserve critical recovery space; fair command/state/history service | Finite values and overload behavior per implementation; reject unavailable capacity before acceptance; synthetic-peer/resource fixtures |
| NFR-06 | Authenticate and authorize peers/operators; verify signed inputs; protect keys/state from workloads; validate IDs/paths/versions | Wrong-peer/key/assignment, tamper, expiry, CSRF, unsafe-path and real OS permission tests |
| NFR-07 | Keep contracts migratable and documentation consistent with real evidence | Schema/protocol compatibility tests, ADR and traceability review |

Exact limits and supported Linux host requirements must be specified and tested
when their implementation arrives. These are testable goals, not current service
levels or a promise of deterministic real-time execution.

## Security and exclusions

The initial [threat model](../architecture/security.md) covers network
attackers, unauthorized or misassigned peers, tampered release/instruction
inputs, compromised workloads and bounded resource abuse. Local trust is
explicitly provisioned; CA membership or knowing an ID alone grants no
deployment permission. Production enrollment, automated credential/revocation
infrastructure, protected production signing, enterprise IAM and independent
security review remain deferred.

The MVP excludes discovery, gossip, CRDTs, multi-writer execution, relays, edge
artifact transfer, advanced rollout scheduling, Gazebo, hardware/navigation and
physical pilots, organization/role management, PostgreSQL, hosted services, IaC,
central telemetry and agent self-upgrade. Real ROS 2 and essential
authentication, authorization, signatures and privilege separation are part of
the MVP.

No cross-resource atomic deployment, zero downtime, exactly-once execution,
physical safety, indefinite audit history or production capacity is promised.
Three real agents plus synthetic peers establish correctness/resource bounds;
millions of assets/devices require future measured evidence.

## Future capability boundaries

All twelve IDs remain deferred until explicitly activated. The [future
architecture](../architecture/future.md) owns their constraints and evidence
gates; the [roadmap](../roadmap.md#future-platform) links delivery milestones.

| ID | Capability boundary |
| --- | --- |
| FUT-01 | Authenticated discovery/membership, justified alternate transports, NAT and optional relays extending secure direct WSS |
| FUT-02 | Signed/authorized selected-state replication and anti-entropy; per-type conflicts and device-fenced authority transfer |
| FUT-03 | Authorized content-addressed artifacts, resumable P2P delivery and peer/edge caches protecting local execution |
| FUT-04 | Canaries/waves, fresh-health gates, scheduling, safe concurrency, pause/resume and rollout UI |
| FUT-05 | Extend MVP ROS 2 into selected Gazebo/advanced robotics and security/platform/safety-gated physical pilots |
| FUT-06 | Production enrollment, credential lifecycle, signing/metadata hardening, incident runbooks and independent security review |
| FUT-07 | Optional bounded OTel/log/metric/trace export, storage, dashboards and alerts independent of execution |
| FUT-08 | Validated native/ARM64 matrix, installation/boot supervision and compatible agent/schema upgrade recovery |
| FUT-09 | Organizations/roles/delegation, isolation/quotas at all boundaries, ownership transfer and historical privacy |
| FUT-10 | Optional central API/PostgreSQL with tenant context from the first migration, administration, projections and explicit authority placement |
| FUT-11 | Service-driven provider/IaC evaluation, isolated environments, managed resources, delivery, secrets/teardown and backup drills |
| FUT-12 | Measured hosted API/jobs/gateways/ingestion/blob architecture, tenant placement/cells, reliability and cost guardrails |

Hardened device operations and peer reachability/artifact delivery take priority
after MVP; SaaS stays optional. Future numbering is thematic rather than an
implementation sequence. No mandatory site gateway or global all-to-all mesh is
introduced by these evolution paths.
