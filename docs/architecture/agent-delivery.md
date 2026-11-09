# Agent delivery, installation and upgrades

**Status:** Accepted intended architecture under #147 and
[ADR 0009](../adr/0009-pixi-agent-delivery.md). Bootstrap, helper and upgrade
recovery are not implemented. Current Linux x86_64 source builds use bundled
SQLite under [ADR 0008](../adr/0008-agent-sqlite-storage.md).
[Agent artifact v1](../specs/agent-releases.md) owns exact metadata, signatures,
activation scope and compatibility rules. Workload release v1 remains unchanged.

## Four lifecycle owners

| Lifecycle                       | Owner                                                         | Boundary                                                                                |
| ------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Device identity and assignment  | Trusted deployment provisioning                               | Persistent device identity, credentials, assignment and policy; replacement is explicit |
| Agent installation and recovery | Independent FleetForge Bootstrap and narrow privileged helper | Verify, stage, activate and recover agent environments; preserve device state           |
| Workload deployment             | FleetForge agent                                              | Prepare, run, verify and recover authorized workload releases                           |
| OS and boot                     | OS provisioning/update adapter                                | Kernel, drivers, root filesystem, boot confirmation and Bootstrap repair                |

Logical owners do not require separate network services. Neither the agent nor
Bootstrap owns OS replacement. A publisher approves bytes; a separately scoped
activation authority authorizes agent replacement. Workload deployment authority
does not implicitly authorize agent or OS updates.

## Installation unit and protected paths

Deliver a prebuilt agent in its own locked Pixi environment. pixi-pack and
Pixi-managed SQLite remain candidates gated by #145; retain bundled SQLite
until that experiment validates a replacement. Build packages for each target in
CI/development, never during device startup. Normal startup uses an already
installed runtime without solve, download, installation or interactive activation.
The root `device` environment remains development tooling. Contributor-host
support is independent of device support.

These are intended Linux provisioning paths, not paths created by today's CLI:

| Resource                                                   | Intended path and writer                                                            |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Device configuration/assignment                            | `/etc/fleetforge/device/`; root provisioner, agent/Bootstrap read                   |
| Agent publisher trust                                      | `/etc/fleetforge/trust/agent-publishers/`; root provisioner, helper read            |
| Activation trust/scope policy                              | `/etc/fleetforge/trust/agent-activation/`; root provisioner, helper read            |
| Workload publisher trust                                   | `/etc/fleetforge/trust/workloads/`; root provisioner, agent read                    |
| Agent credentials                                          | `/etc/fleetforge/credentials/agent/`; provisioner writes, agent principal reads     |
| Bootstrap credentials, if remote repair is later activated | `/etc/fleetforge/credentials/bootstrap/`; separate principal and grants             |
| Agent identity DB and operational state                    | `/var/lib/fleetforge/agent/`; agent writes                                          |
| Bootstrap journal and anti-replay/policy state             | `/var/lib/fleetforge/bootstrap/`; helper writes, manager gets bounded results       |
| Immutable installed agents                                 | `/opt/fleetforge/agents/<artifact-digest-hex>/`; helper installs/seals, agent reads |
| Bootstrap executable and helper                            | `/usr/libexec/fleetforge-bootstrap/`; OS provisioner writes                         |
| Helper socket and coordination state                       | `/run/fleetforge-bootstrap/`; OS-created protected directory                        |

The layout separates files by lifetime and update owner:

- `/etc` holds provisioned configuration, trust and credentials.
- `/var/lib` holds mutable records that must survive reboot and software replacement.
- `/opt` keeps separately delivered agent environments together, with one directory
  per artifact so current and recovery versions can coexist.
- `/usr/libexec` holds internal programs supplied by OS provisioning, keeping
  Bootstrap and its helper outside the agent environment they must recover.
- `/run` holds sockets and locks recreated at boot; durable maintenance progress
  belongs in the Bootstrap journal under `/var/lib`.

These are FleetForge's intended Linux deployment choices. The
[Linux hierarchy reference](https://uapi-group.org/specifications/specs/linux_file_system_hierarchy/)
explains the configuration/state/runtime distinction; it recommends `/usr/lib`
for newer third-party integration rather than `/opt`. #145 must validate this
separately delivered environment layout, and native packaging must confirm the
OS-specific internal executable location. Directory names alone enforce no
permissions: provisioning must establish the ownership shown above.

An agent environment cannot contain its own sole recovery binary, Bootstrap
journal or identity DB. Bootstrap needs only bounded schema inspection through
a read-only DB handle; it cannot regenerate identity or modify workload intent.
No workload user can write these paths or read management credentials.
Agent and Bootstrap principals cannot replace the helper, OS-owned Bootstrap
binary, trust stores or sealed installations. Helper and OS provisioning enforce
ownership and race-resistant traversal. #87/#145 establish executable permissions
and layout evidence; this table supplies their contract, not security evidence.
The existing configurable #16 state directory is not migrated by #147.

## Bootstrap and narrow helper

Build/version Bootstrap independently of the agent package, with its own runtime
and dependencies provisioned by the OS installer. A broken agent environment,
missing agent libraries or corrupt agent DB must not prevent Bootstrap startup.
Initial trusted factory/customer installation provisions Bootstrap/helper, local
policy, identity, journal, recovery inputs and service units before agent start.
OS packages/provisioning repair Bootstrap conservatively from retained trusted
inputs; Bootstrap cannot overwrite itself or the OS. No automatic self-upgrade
is implied. Ansible and systemd remain deployment/service candidates with
platform evidence required by later deliveries.

The unprivileged Bootstrap manager requests fixed operations over an OS-owned
local socket. The helper verifies kernel peer credentials against a provisioned
manager UID, bounds request size/concurrency and revalidates protected policy,
signed artifact and signed activation itself. Socket possession or a manager's
assertion that verification succeeded is insufficient. No network listener,
remote argv, arbitrary path, shell text, environment variables or library paths
are accepted by the helper.

The helper accepts only `inspect`, `stage`, `activate` and `recover` requests
identified by artifact/instruction digest and transaction ID. It resolves inputs
from a provisioner-owned inbox and derives all destinations from protected roots.
`recover` refers only to the recorded retained artifact of that transaction;
it cannot select arbitrary older software or bypass current policy. Fixed service
operations address only provisioned agent units. The OS installer separately owns
cleanup and Bootstrap maintenance. Unpacking hooks run with a staging principal
without helper/root credentials; never run publisher code with helper privileges.
Unsupported archive/unpacker behavior fails closed before service changes.

## Exclusive maintenance and replacement

Agent replacement must not overlap a workload deployment or recovery. Otherwise,
the agent could be stopped while changing the workload, leaving neither owner
able to finish that change. The handoff uses two local mechanisms:

- An exclusive OS file lock allows only one owner to change agent/workload state
  at a time. The agent deployment coordinator holds it during workload transitions;
  Bootstrap holds it during agent replacement.
- A protected, durable maintenance-pending record tells the agent to pause new
  workload transitions. It preserves that pause across process crashes and reboot.
  Only the helper may create or clear it.

The handoff proceeds as follows:

1. After artifact and compatibility preflight, the helper records maintenance
   pending. This requests a pause; it does not yet accept the activation instruction
   or change its generation counter.
2. The agent finishes or safely aborts its current transition, then stops workloads
   and probes while holding the lock. It acknowledges that they have stopped,
   releases the lock, and remains paused. Before every new transition it checks
   the pending record while holding the lock.
3. Bootstrap acquires the lock, independently verifies that no owned children
   remain, rechecks authorization and compatibility, and durably accepts the update.
   It then stops the old agent, selects the candidate and checks its readiness.
4. Bootstrap keeps the lock and pause in place until the candidate is ready or the
   retained agent has recovered. The helper records the outcome, clears the pause
   and releases the lock. The selected agent can then reconcile accepted workload
   intent and restart workloads with fresh health checks.

If admission fails before replacement, the helper reconciles and clears the
pending record so the current agent can resume. If replacement or recovery fails,
it leaves the pause in place for repair. The OS releases a crashed process's file
lock, but the durable pending record still blocks new workload transitions.
At boot, the helper reconciles its journal before allowing the agent to resume.
A timeout never authorizes taking a lock from a live owner. The record has no
expiry: recovery must establish which state is safe before clearing it.

For the initial contract, agent replacement requires stopping all managed
workloads and probes with bounded graceful stop, kill and reap under agent
coordination. Verify owned children are absent before stopping the agent. No
adoption or uninterrupted supervision is claimed. If the agent is unavailable,
Bootstrap uses only the OS-provisioned dedicated workload containment unit;
it must establish that unit empty, or reject replacement. Never signal a PID
from stale DB data. #17/#19 must implement matching process/maintenance admission.

After restart the selected agent reads durable accepted workload intent and
reconciles under the same lock with fresh process identities and actual health
checks. Agent readiness means validated identity/storage and a functioning
coordinator ready to reconcile; it does not assert healthy workload execution.
A fresh attempt token binds readiness to the started candidate process, with a
local finite deadline. The helper checks OS process ownership as well as this
response; a stale ready file cannot complete activation.

## Durable switching and recovery

The helper owns a single serialized journal transaction: verified/staged,
accepted/quiescing, selected, verifying, committed; on failure, recovering,
recovered or recovery-failed. Persist the selected and retained artifact digests,
instruction digest/generation, policy floor, schema plan and phase before each
external effect, with file/directory durability appropriate to the target.
An atomic selection record chooses a sealed installation; no in-place overwrite.
Replay counters survive failed activation. Retry the same transaction idempotently.

| Interruption/failure                                        | Required next action                                                                           |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Before acceptance                                           | Keep current agent; discard only unaccepted staging under explicit retention policy            |
| Accepted, before selection                                  | Reconcile child containment and finish the recorded selection or recover                       |
| Selection durable, candidate not ready                      | Start/inspect that exact candidate within budget; on failure recover retained compatible agent |
| Candidate readiness verified                                | Durably commit success before allowing workload transitions                                    |
| Recovery interrupted                                        | Resume the recorded recovery; never allocate a new generation implicitly                       |
| Recovery incompatible, untrusted, absent or fails readiness | Record recovery-failed; keep workload admission fenced and expose local repair status          |
| Journal corrupt or selection ambiguous                      | Fail closed for repair; preserve inputs and identity                                           |

Candidate schema migration cannot make the retained agent unusable. Validate
read/write ranges and planned target before acceptance; runtime migration must
be transactional and constrained to that target. Automatic DB restore could
lose accepted work and is forbidden by this contract. Retain current and recovery
inputs until a later explicit retention decision preserves a permitted recovery
path. Boot always reconciles the journal before ordinary agent/workload startup.

## Platform and delivery evidence

Native Linux AMD64 and ARM64 are intended foundation targets. #69 owns measured
OS/ABI profiles and #148 native builds/storage failures. Packing foreign
packages is not compilation or native execution evidence. No operational device
matrix expands through this document alone; MVP workloads remain `linux-64`.

#147 owns contract adoption, #69/#148 profiles/native evidence, then #145 the
packaging/shared-SQLite and safe unpacker/layout gate before #87 runtime
permissions. #31/#32 consume validated artifacts for MVP simulation. The
independent local Bootstrap VM proof (#149/#70/#103/#72/#104) is the first
post-M8 delivery; it remains deferred until explicitly activated.
Production enrollment, remote repair and OS updates have their own gates.

The [official Pixi pack documentation](https://pixi.prefix.dev/latest/deployment/pixi_pack/)
was consulted on 2026-11-09. It describes environment transport/reconstruction,
not FleetForge authorization or recovery. The project minimum remains Pixi 0.83.0 (the checking host used 0.84.1); no pack
version or safe-unpacker compatibility is established here. #145 must pin and
measure these before adoption, preserving an actionable reproducer if unsupported.
