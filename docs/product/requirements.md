# Product requirements

**Status:** Accepted product direction; implementation and verification are
delivered through the linked GitHub work. This file defines the contract, not
current software capabilities.

## Vision and operating model

FleetForge is an open-source, Pixi-native robotics software deployment and fleet
management platform. An operator declares desired software; each robot owns its
operational state, execution, health verification, and recovery.

Robots may work in laboratories, factories, warehouses, or remote sites with
unreliable connectivity. Accepted work must not require a continuously reachable
operator when its software inputs and resources are already local.

There are three scopes:

1. **Bootstrap:** reproducible engineering tooling and documentation. It is not
   the functional MVP.
2. **Functional MVP:** a real deployment lifecycle across three simulated robots,
   one operator, and a functional console.
3. **Future platform:** capability expansions with separate decision gates.

## Domain terminology

| Term | Meaning |
| --- | --- |
| Robot identity | Stable globally unique identifier, separate from address and future ownership |
| Operator authority | The single persisted identity allowed to issue MVP desired state |
| Fleet | Configured group of robot identities and separately configured addresses |
| Release | Immutable descriptor, application files, Pixi manifest, and Pixi lockfile |
| Release catalog | Explicit mapping from supported release IDs to immutable descriptors/digests |
| Desired state | Target release and integrity information for a robot at a generation |
| Generation | Durable, monotonically increasing counter per robot under the operator authority |
| Request ID | Identity used to recognize retries of an operator submission/instruction |
| Acceptance | Robot has validated and durably stored an instruction; execution may still be pending |
| Deployment attempt | Correlated effort to satisfy an accepted desired-state generation |
| Active release | Release associated with the actual managed workload; absent/unknown are explicit possibilities |
| Known-good release | A release that previously passed workload health verification |
| Automatic recovery | Agent restores and verifies known-good software after a failed deployment |
| Requested rollback | Operator issues a new generation targeting a previous release |
| Observed status | Robot snapshot last received by the operator, with identity, sequence, and freshness |
| Durable event | Bounded persisted operational history, distinct from application stdout and security audit |

## Fixed MVP boundary

| Concern | Contract |
| --- | --- |
| Operating model | Local-first, single-tenant, trusted local development |
| Authority | One Rust operator with SQLite persistence |
| Robots | Three independent Rust/Tokio agents with separate SQLite state |
| Software | Two real immutable releases, A and B, in release-owned Pixi environments |
| Release availability | Pre-provisioned manifests, files, and dependency package caches |
| Networking | Direct communication at configured peer addresses |
| Deployment | Separate preparation, activation, health verification, and recovery |
| Interface | SvelteKit/TypeScript console over the Rust operator API |
| Simulation | Docker Compose; independent identities, databases, runtimes, and caches |
| Visibility | Structured logs, durable events, status API, recent history, and freshness |
| Target | Linux x86-64 development and simulation baseline, subject to validation |

## Functional requirements

### MVP-01 — Engineering foundation

Provide root Pixi and virtual Cargo workspaces, one meaningful Rust executable,
reproducible toolchain/lockfiles, canonical tasks, GitHub Actions, license,
contribution/agent conventions, initial ADRs, and GitHub-linked planning.

Use separate Pixi `dev` and `build` environments with shared toolchain features.
Development includes Pixi-managed prek and Commitizen. Use `prek.toml`, local
pre-commit and commit-msg hooks, and matching CI validation. Introduce Ruff
linting/formatting and mypy with the first Python code; keep them out of deployed
workloads. Rust uses rustfmt and Clippy. Checks must preserve tracked sources and
lockfiles; format/fix are explicitly mutating. Cleaning must preserve operational
state. Add tasks and packages only when they perform meaningful work.

**Acceptance:** a contributor can clone, install the locked environment, build
and invoke the executable, and reproduce formatting, linting, tests, and CI.
Bootstrap requires no SQLite, peer networking, web app, deployment engine, or
purpose-free infrastructure.

### MVP-02 — Reproducible software releases

Provide independent A/B releases of a small real Python workload. Each has a
stable ID, manifest, lockfile, files, executable entrypoint, health contract,
immutable descriptor, and integrity information. Operator and robots agree on
the explicit catalog. Unknown, missing, or mismatched releases fail clearly.

**Acceptance:** fresh installed environments execute genuinely different
application behavior, not only different version metadata; health identifies the
running release and process instance.

### MVP-03 — Durable robot agent

Provide stable identity, configuration, SQLite migrations, supervised processes,
liveness, workload health, structured logs, and recovery-capable startup. As
lifecycle concepts arrive, persist desired state/generation, attempt, active and
known-good release, and recovery metadata.

**Acceptance:** restart preserves identity and critical operational state; the
agent inspects durable state and real process/filesystem evidence before acting.

### MVP-04 — Local deployment lifecycle

Resolve local releases, validate integrity, prepare Pixi environments separately,
activate real processes, verify workload health, report success, and recover to
known-good software on activation/verification failure. Failed recovery is an
explicit outcome. Retain A for recovery and later rollback even after B succeeds.

**Acceptance:** deploy B from A; a real failing B health check restores verified A.
Preparation failure preserves healthy A. Failed recovery is observable, and
terminal failed generations do not create endless deploy/recover loops.

### MVP-05 — Direct operator communication

One Rust operator addresses three configured agents, sends desired-state
instructions, receives durable acceptance acknowledgments and actual status, and
handles disconnection/reconnection.

**Acceptance:** a reachable robot persists accepted intent and reports real state.
Sending a request is never presented as proof of acceptance or deployment success.

### MVP-06 — Declarative reconciliation

Persist operator authority, per-robot desired intent, request IDs, and increasing
generations. Version messages, deduplicate instructions, reject stale generations
and equal-generation conflicts, reconcile after restart, and synchronize status
on reconnect. A newer generation targeting already healthy active software is
satisfied without unnecessary process replacement.

**Acceptance:** retries, duplicates, stale/conflicting messages, lost
acknowledgments, and restarts cause no unintended deployments or generation reuse.
Requested rollback to A is a new generation.

### MVP-07 — Operational observability

Introduce diagnostics with the operational agent, then extend them with each
capability. Include component/robot/operator identity, request/attempt correlation,
release, generation, phase, timestamps, meaningful error codes/messages, and useful
durations. Persist significant lifecycle events with deduplication identifiers.

Expose liveness separately from workload health, desired/accepted/active state,
current progress, last outcome, recovery, last contact, and bounded recent history.
Bound general output handling separately. Report event retention gaps; do not
promise indefinite history or exactly-once event delivery.

**Acceptance:** each demonstrated deployment can be explained from request to
acceptance, execution, failure/success, actual active release, and recovery.
Disconnected status is labelled last observed, never current certainty.

### MVP-08 — Independent simulated fleet

Run three agents and one operator in Docker Compose, adding the frontend when
implemented. Give robots separate identity, SQLite, runtime directories, caches,
and relevant mutable release storage. Configure direct addresses and controlled
network/health/process faults. Normal shutdown preserves persistent state; reset
is separate and explicit.

**Acceptance:** robots demonstrate different outcomes without accidental shared
state, and deterministic scenarios clean up only their own resources.

### MVP-09 — Functional operator console

SvelteKit displays actual Rust operator observations: identity, contact/freshness,
connectivity, liveness, workload health, active/desired release, generation,
progress, recent events, errors, and recovery. Provide deploy-B, inspection, and
rollback-to-A controls. Represent independent per-robot outcomes and partial
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

Existing workloads continue without public internet. Agent/container restart may
interrupt the workload during recovery; uninterrupted execution is not promised.
A lockfile identifies dependencies but does not supply their package bytes. An
already installed B environment is not evidence of fresh offline installation.

**Acceptance:** each scenario proves the intended allowed/blocked paths and real
process outcomes rather than relying on configuration flags or database labels.

### MVP-11 — Complete reproducible demonstration

Automate and document seven phases using independent or explicitly reset fixtures:

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
| NFR-05 | Bound queues, subprocess output, timeouts, retries, and retained history | Capacity/failure fixtures appropriate to each implementation |
| NFR-06 | Validate input, IDs, paths, and protocol versions; avoid arbitrary remote shell execution and public controls | Negative contract/path tests and network-exposure checks |
| NFR-07 | Keep contracts migratable and documentation consistent with real evidence | Schema/protocol compatibility tests, ADR and traceability review |

Exact limits and supported Linux host requirements must be specified and tested
when their implementation arrives. These are testable goals, not current service
levels or a promise of deterministic real-time execution.

## Security and exclusions

The MVP assumes trusted local peers. Restrict exposed control ports, validate
messages and local paths, pass executable arguments explicitly, keep secrets out
of source/logs, and distinguish integrity hashes from trusted publisher signatures.
Production authentication, enrollment, authorization, signing, secure distribution,
secret lifecycle, and security audit require future work before untrusted use.

The MVP has no discovery, gossip, CRDTs, multi-master authority, consensus, relays,
edge peer, artifact transfer, advanced rollout scheduler, ROS 2, physical robots,
multi-tenancy, PostgreSQL, cloud hosting, IaC, centralized telemetry platform, or
agent self-upgrade. It claims neither transactional cross-resource deployment,
zero downtime, exactly-once distributed delivery, nor physical robot safety.

## Future capability boundaries

These IDs describe deferred scope. The [roadmap](../roadmap.md) links their live
GitHub delivery owners and dependencies; numbering is thematic, not chronological.

| ID | Capability boundary |
| --- | --- |
| FUT-01 | Discovery/dynamic membership, QUIC evaluation, NAT traversal, relays, authenticated transport |
| FUT-02 | Gossip, anti-entropy, multi-site convergence, partition recovery, conflict resolution, justified CRDTs |
| FUT-03 | Content-addressed artifacts, resumable P2P delivery, deduplication, edge caching, provenance/authorization |
| FUT-04 | Canaries, rolling/wave deployment, concurrency, scheduling, health gates, pause/resume and policies |
| FUT-05 | ROS 2, RoboStack, Gazebo, lifecycle/diagnostics, robot workloads and bounded physical pilots |
| FUT-06 | Production threat model, enrollment, authentication, authorization, signed releases, secrets, security audit |
| FUT-07 | OpenTelemetry, metrics/traces/log storage, alerting, reliability dashboards and analytics |
| FUT-08 | ARM64/embedded Linux, native installation, service supervision, agent upgrades and hardware recovery |
| FUT-09 | Organizations/roles, tenant ownership, isolation at every boundary and safe device transfer |
| FUT-10 | Optional central API/PostgreSQL, fleet/site inventory, histories, metadata, administration and reporting |
| FUT-11 | Provider/IaC evaluation, managed storage/database, networking, secrets, CI/CD, backup and environments |
| FUT-12 | Workload-specific cloud runtime evaluation, persistent gateways, scale, availability, disaster recovery and cost |

Production security precedes untrusted operation and shared multi-tenant use.
Physical support requires validated device/safety boundaries. Central services
store projections and administrative data; robot-local SQLite retains execution
and recovery authority. Large artifact bytes belong in appropriate object/artifact
storage rather than defaulting to PostgreSQL. Cloud runtime/provider/IaC choices
remain workload-driven decisions. Stable globally unique identity, versioned
protocols, migratable schemas, and separation of ownership/authorization/execution
preserve evolution paths without implementing tenant schemas prematurely.
