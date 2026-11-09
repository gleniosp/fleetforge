# Provisioning identity and running the agent

The agent is the FleetForge process that runs on a managed computer. Today it
can persist and validate its identity and assignment in SQLite, report that its
event loop is alive, and stop cleanly. You can try this on a Linux x86_64
contributor host without a robot or authority server.

## Where this fits in FleetForge

Before an authority can ask a robot to run software, both sides need to agree on
which robot and computer they mean, who owns them, and which authority may
manage them. Provisioning means preparing those records and the files the
device needs before normal operation.

Consider a robot named Rover with an onboard computer:

| Record           | What it identifies                                 | When to allocate it                                                           |
| ---------------- | -------------------------------------------------- | ----------------------------------------------------------------------------- |
| `asset_id`       | Rover, the maintainable robot                      | Once for this robot; retain it if the computer is replaced                    |
| `device_id`      | Rover's onboard computer                           | Once for this managed computer; replacement or cloned computers need a new ID |
| `tenant_id`      | The owner                                          | Reuse the owner's ID across its robots                                        |
| `authority_id`   | The logical service allowed to request deployments | Reuse it for devices managed by that authority                                |
| `assignment_id`  | The relationship between these four records        | Allocate for this assignment; retain it across ordinary restarts              |
| `agent_instance` | One running agent process                          | The agent generates a fresh value each time it starts                         |

Names such as Rover are useful labels; they are not identity or permission.
The [identity contract](../architecture/identity.md) owns replacement, cloning,
recovery and retention rules.

The intended workflow is:

1. **Prepare identity and assignment.** An operator allocates IDs where needed,
   checks them against their inventory, and writes the device configuration.
   The current CLI supports local ID allocation and configuration checks.
2. **Persist and protect the device records.** Startup persists identity in SQLite. Planned M2 work adds
   credentials, trusted keys and workload/agent file permissions.
   Identity records alone do not establish these protections.
3. **Prepare approved software inputs.** Release tooling signs and provisions
   release files and dependency bytes. See [release provisioning](release-provisioning.md).
   Software provisioning and device identity provisioning prepare different inputs;
   both are needed before a complete deployment scenario.
4. **Run the agent and establish authorized communication.** Today the agent
   reports local liveness. Device-initiated authenticated connections, authority
   registry checks and signed instructions are planned M4 work.
5. **Deploy and observe software.** The completed agent will durably accept an
   authorized request, prepare the release, supervise its process, verify health
   and recover on failure. See the [deployment walkthrough](releases-explained.md).
   These deployment capabilities still need implementation.

The steps above explain the operational flow, not the order in which project
issues must be implemented. The [project README](../../README.md#current-state)
owns the current capability summary.

For the planned agent software replacement flow, read the
[agent release examples](agent-releases-explained.md). They explain artifact
approval and activation separately from the identity/startup steps above.

## Diagnostic versus configured execution

With no arguments, `agent-run` prints the bootstrap diagnostic and exits:

```sh
pixi run --locked -e device agent-run
```

This mode does not read configuration or create identity state. The demonstration
below uses `--new-id` to provision ID files, then `--config` to run the agent and
initialize or validate its SQLite store.

## Try it locally

Run these commands from the repository root on Linux x86_64. They create a
separate temporary directory for this demonstration and generate IDs for a new
example owner, authority, robot, computer and assignment.

```sh
demo_dir=$(mktemp -d /tmp/fleetforge-agent.XXXXXX)
mkdir "$demo_dir/state" "$demo_dir/runtime"

for identity in asset device tenant authority assignment; do
    pixi run --locked -e device agent-run -- --new-id "$demo_dir/$identity.id"
done

cat "$demo_dir/device.id"
```

Each ID file contains one uppercase ULID: a 26-character identifier. The
`--new-id` command creates a file exclusively and refuses to overwrite an
existing destination. It does not register or enroll anything. In a real setup,
keep these records in your operator inventory and reuse existing tenant and
authority IDs where appropriate.

Create the configuration using the IDs you just generated:

```sh
cat > "$demo_dir/agent.toml" <<EOF_CONFIG
asset_id = "$(cat "$demo_dir/asset.id")"
device_id = "$(cat "$demo_dir/device.id")"
state_dir = "$demo_dir/state"
runtime_dir = "$demo_dir/runtime"
authority_endpoint = "wss://localhost:8443/agent"

[assignment]
asset_id = "$(cat "$demo_dir/asset.id")"
device_id = "$(cat "$demo_dir/device.id")"
tenant_id = "$(cat "$demo_dir/tenant.id")"
authority_id = "$(cat "$demo_dir/authority.id")"
assignment_id = "$(cat "$demo_dir/assignment.id")"
EOF_CONFIG
```

The top-level asset/device IDs say which agent this is. The same fields inside
`[assignment]` say which asset and device the relationship binds. Repeating them
lets the agent reject an assignment copied from another device by mistake.
Both copies must match. This is a local consistency check: someone who changes
both copies can still produce a consistent file. Authorization requires the
trusted configuration, credentials, registry and signature checks described in
[security](../architecture/security.md); those runtime checks are not delivered
by this configuration parser.

Start the agent:

```sh
pixi run --locked -e device agent-run -- --config "$demo_dir/agent.toml"
```

No server needs to listen on port 8443. The endpoint is checked for valid `wss`
syntax but is not contacted. The state and runtime directories must exist and be
separate. First configured startup creates the identity store beneath the state
directory; subsequent startups validate it. The current agent creates no files
in the runtime directory. The [specification](../specs/agent.md) owns the full
validation rules and startup limits.

## Read the output and stop the process

The agent writes JSON diagnostic events to stderr. Look for these values in
`fields.code`:

| Event            | What you should observe                                        |
| ---------------- | -------------------------------------------------------------- |
| `agent_started`  | Identity storage succeeded and the event loop is running       |
| `agent_liveness` | A heartbeat appears immediately, then about every five seconds |
| `agent_stopped`  | Ctrl-C or SIGTERM caused a normal shutdown                     |

The event's span carries asset/device, tenant, authority, assignment and agent
instance IDs. A span is a named execution context that groups related events.
We use Rust's `tracing` library to produce these structured logs with shared
context. The current output is local JSON; there is no distributed trace
collector or operation timing dashboard.

`liveness = "alive"` means the agent loop is running. It does not establish robot
application health: `workload_process = "absent"` and
`workload_health = "unknown"` are expected because this agent does not yet manage
a workload. The separate ROS release fixtures can run workloads, but are not
connected to this agent yet. Output uses a bounded queue and can drop events if
the sink stalls, so it is not durable history.

Press **Ctrl-C** to stop the process, then run the same command again. The
configured IDs should remain unchanged and `agent_instance` should change.
Stop the agent again before inspecting the files below.
Startup now persists identity and assignment in SQLite and rejects changes to
stored bindings. Preserve the configuration, inventory records and complete
state directory beyond this temporary demonstration; see
[storage recovery](../specs/agent-storage.md#creation-and-reopening).

## Inspect the generated files

After successful configured startup, the demonstration directory contains:

```text
$demo_dir/
├── agent.toml
├── asset.id
├── device.id
├── tenant.id
├── authority.id
├── assignment.id
├── state/
│   └── identity-store/
│       └── identity.sqlite3
└── runtime/
```

The ID files and configuration are inputs created by the earlier provisioning
commands. Configured execution leaves their contents intact and creates the
SQLite store. The database records schema version, asset/device IDs and the
tenant/authority/assignment binding. The schema migration is embedded in the
executable; no SQL file is generated here.

Inspect the state and runtime directories without installing a SQLite CLI:

```sh
ls -la "$demo_dir/state/identity-store" "$demo_dir/runtime"
```

SQLite may also create `identity.sqlite3-wal` and `identity.sqlite3-shm` sidecars
during startup. The agent closes its database connection before entering the
liveness loop, so these normally disappear after successful initialization;
they may remain after interruption. Preserve the whole state directory during
recovery, including any sidecars.

On restart, the existing store must match configuration. A missing database
inside `identity-store/`, an incomplete initialization or damaged state rejects
startup before `agent_started`. The retained directory marks prior initialization;
do not delete it merely to retry. See
[storage recovery](../specs/agent-storage.md#creation-and-reopening).

JSON diagnostics go to stderr; the agent does not create a log file. The runtime
directory remains empty in this slice.

## Check failure behavior

In the same shell, print the configuration path so you can open it in an editor:

```sh
printf '%s\n' "$demo_dir/agent.toml"
```

Try one change at a time, run the agent again, and restore the file before the
next change:

| Change                                                                     | Expected result                       |
| -------------------------------------------------------------------------- | ------------------------------------- |
| Replace only the top-level `device_id` with the existing `tenant_id` value | `identity does not match assignment`  |
| Change `device_id` in both locations to the existing `tenant_id` value     | Stored `identity/assignment mismatch` |
| Change one ID to lowercase                                                 | `invalid configuration schema or ID`  |
| Change `wss://` to `ws://`                                                 | Endpoint validation fails             |
| Set `runtime_dir` to the same value as `state_dir`                         | Directory validation fails            |

Configuration or identity-store failures exit with status 1. Check the status immediately after
the command with `echo $?`.

You can also check that provisioning preserves an existing identity file:

```sh
pixi run --locked -e device agent-run -- --new-id "$demo_dir/device.id"
cat "$demo_dir/device.id"
```

The command should report a provisioning conflict; the ID should be unchanged.
When finished, the temporary directory printed by `printf '%s\n' "$demo_dir"`
contains this demonstration's configuration, ID files and SQLite store. Remove
this disposable example only when you no longer need its records; retain the
complete state directory for any identity you intend to reuse.

## Run the automated checks

```sh
pixi run --locked -e device agent-test
pixi run --locked -e device agent-check
```

The tests cover ID parsing, configuration rejection, provisioning conflicts,
real signal shutdown, fresh process instance identity, durable restart, damaged
state rejection and a stalled startup.
The [foundation journal](../journal/2026-11-03-agent-identity.md) and
[storage journal](../journal/2026-11-04-agent-storage.md) record results and
verification limits.

Retain configuration and the complete state directory across restarts. The
[storage specification](../specs/agent-storage.md) explains mismatch and damaged-store
recovery. Changing configured identity requires explicit recovery/provisioning.

The [agent delivery contract](../architecture/agent-delivery.md) describes the
intended dedicated Pixi runtime. Its packaging validation is #145; the commands
in this guide currently build/run the agent from source.
