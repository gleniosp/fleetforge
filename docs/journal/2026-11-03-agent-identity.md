# Agent identity and configured liveness foundation

Delivery: [#15](https://github.com/gleniosp/fleetforge/issues/15).
Source: uncommitted working tree on `feat/15-asset-device-identity`, based on
`a67c320aeb6fb5a380eafad8783eed6355604e47`. This record describes local evidence,
not a merged delivery or complete M2 foundation.

## Delivered behavior

Distinct Rust asset/device types enforce canonical uppercase ULIDs. Explicit
exclusive-file provisioning uses OS entropy and rejects existing destinations.
Configuration binds asset/device to separate tenant/authority/assignment context,
checks paths and the outbound WSS endpoint, and rejects malformed or oversized
input without quoting TOML contents. The Tokio process emits correlated JSON
startup/liveness/shutdown events and handles SIGINT/SIGTERM. Workload process is
absent and health unknown. The [specification](../specs/agent.md) owns exact
limits and the [guide](../guides/agent.md) owns invocation.

## Dependencies and compatibility

Cargo's [dependency reference](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html)
and [metadata reference](https://doc.rust-lang.org/cargo/commands/cargo-metadata.html)
were consulted on 2026-11-03. Cargo 1.98.1 resolved and compiled the lock with
Rust 1.98.1, the project toolchain; Pixi configuration and host/device boundaries
were unchanged. No new host executable prerequisite is needed for the agent.
The Linux stalled-I/O test uses the reference host's `mkfifo` utility.

Each new direct dependency has a present runtime role:

| Dependency         | Locked version | Role                                                                              |
| ------------------ | -------------- | --------------------------------------------------------------------------------- |
| getrandom          | 0.3.4          | Fallible OS entropy; no panic on entropy failure                                  |
| ulid               | 1.2.1          | ULID encoding and timestamp layout; strict canonical boundary is FleetForge-owned |
| serde              | 1.0.229        | Typed configuration deserialization                                               |
| toml               | 0.9.12         | Bounded TOML configuration parsing                                                |
| http               | 1.5.0          | URI grammar; explicit FleetForge port/scheme/credential/fragment checks           |
| tokio              | 1.54.1         | Single-thread event loop, signals, timers and bounded startup worker              |
| tracing            | 0.1.44         | Correlated event/span fields                                                      |
| tracing-subscriber | 0.3.23         | JSON event serialization                                                          |
| tracing-appender   | 0.2.5          | Bounded lossy writer queue and bounded shutdown flush                             |

`cargo tree -p fleetforge-agent --depth 1` and full locked Cargo metadata were
inspected. The metadata contains 81 packages including the agent and dependencies
for unbuilt targets. All declare licenses, with permissive options available
(MIT/Apache/BSD/Unlicense, Unicode and LLVM exceptions). ULID's `std` feature
brings rand transitively; direct getrandom is retained for fallible entropy.
No independent dependency advisory audit or non-Linux build was performed.

Primary API references: [Tokio shutdown](https://docs.rs/tokio/1.54.1/tokio/runtime/struct.Runtime.html#method.shutdown_timeout),
[tracing nonblocking writer](https://docs.rs/tracing-appender/0.2.5/tracing_appender/non_blocking/index.html).
The locked tracing-appender source was manually inspected for its 100 ms/one
second shutdown handshakes. A startup timeout releases the caller; it cannot
cancel a stalled blocking syscall. The CLI process then exits.

## Validation

Environment: Linux x86_64, host Pixi 0.83.0, Rust 1.98.1
(`48a229cea 2026-09-01`), Cargo 1.98.1 (`797e8a9bc 2026-08-05`).

- `pixi run --locked -e device agent-format`: passed.
- `pixi run --locked -e device agent-test`: passed, 17 tests (3 unit,
  10 existing CLI, 4 configured-process integration tests).
- `pixi run --locked -e device agent-lint`: passed with warnings denied.
- `pixi run --locked -e host format` and `pixi run --locked -e host check`: passed.
  Sandbox cache writes initially failed; rerunning with approval allowed the tools
  to update their caches. Source checks then passed.
- `git diff --check`: passed. New documentation relative file links were checked;
  source and documentation diffs were manually reviewed.

The tests cover known ULID vectors, maximum/overflow, length/alphabet/case,
non-ASCII input, distinct asset/device types, generated IDs, non-overwriting
provisioning conflicts, binding mismatch, same asset/device conflict, invalid
WSS endpoint/port/credentials/fragment, missing/overlapping directories, unknown
fields, malformed IDs and oversize configuration without input disclosure.
Real subprocesses start, report correlated liveness/health distinctions, stop on
both signals and restart with new instance identity and unchanged configuration.
A FIFO with no writer demonstrates the five-second startup deadline plus bounded
runtime worker shutdown: failure exits in about six seconds. Existing CLI
broken-pipe/full-device tests remain passing.

Initial negative tests exposed that URI parsing alone does not reject every
invalid port or fragment. Explicit policy checks fixed both cases before the
passing run. Test subprocess failures now have deadlines to prevent a regression
from hanging validation.

## Limits and review

Identity retention is through explicit configured records and operator inventory;
SQLite persistence and registry uniqueness are not claimed. No credentials,
workload, permission isolation, networking or durable health/event history is
implemented. No entropy-source failure injection, hostile filesystem races,
blocked-log-sink experiment, ROS run or other device platform was verified.
Bounded logging behavior is based on locked library source/API review; final logs
can be dropped. OS permission and trust checks remain #87, persistence #16.

Local review inspected CLI compatibility, strict parser boundaries, assignment
mismatch, exclusive creation, error redaction, startup/shutdown ownership and
bounded logging. No changes are staged or committed.

## Guide walkthrough review

The guide now connects identity provisioning to device persistence/protection,
release provisioning, authorized communication and deployment. It explains reuse
of tenant/authority IDs, the repeated assignment bindings, expected liveness
output and local failure checks. The specification explicitly distinguishes
matching local records from authorization. The release walkthrough links to
this device setup context.

The shell setup/configuration blocks in the guide were executed on the same
Linux x86_64 host. The generated configuration started through the documented
Pixi command; JSON startup/liveness events reported absent workload and unknown
health. Sending SIGINT to the process group (the terminal Ctrl-C behavior) stopped
it successfully with a shutdown event. Repeating startup preserved configured
identity and produced a fresh agent instance. Mismatched device binding, `ws`
endpoint, overlapping directories and re-provisioning an existing ID all failed
as described. The configuration and existing ID were preserved after the checks.
This walkthrough check used automated subprocess control, not a manual terminal
session. No Rust implementation or automated test source changed in this review.
