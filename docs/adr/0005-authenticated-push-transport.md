# ADR 0005 — Direct authenticated push transport

- **Status:** Accepted transport choice; protocol and implementation pending.
- **Date:** 2026-10-20
- **Delivery:** [M4-01](https://github.com/gleniosp/fleetforge/issues/25),
  [M4-07](https://github.com/gleniosp/fleetforge/issues/88).

## Context

Configured devices need desired-state and observation transitions, reconnect and
bounded catch-up without making a broker/cloud service mandatory.
Device-initiated connections fit the selected local topology. Transport
acknowledgment cannot replace durable application acceptance.

## Decision

Use device-initiated direct WebSocket over TLS 1.3 mutual TLS to the configured
local authority, with registry authorization and bidirectional push. Browser
traffic uses a separate authenticated local API and bounded polling of stored
projections. The [coordination contract](../architecture/coordination.md) owns
session, retry, synchronization, expiry and finite-capacity behavior. The
[security contract](../architecture/security.md) owns trust checks.

Agent and authority services use Rust/Tokio; the console uses
SvelteKit/TypeScript. Implementation-library choices must support the selected
transport and its application contracts.

## Alternatives and consequences

HTTP polling can work but is not the selected transition-push model. MQTT is a
valid local/offline broker/pubsub option; the direct MVP topology does not
justify the extra broker. Optional MQTT integration remains possible. QUIC,
discovery, NAT and relays require separate future justification and security
evidence.

Persistent sessions require heartbeats, expiry handling, jittered reconnect and
fair bounded command/state/history work. WSS provides no automatic
discovery/mesh, authority, durable acceptance or exactly-once execution.
Application semantics stay independent of protocol receipt or broker QoS.

## Sources, evidence and revisit conditions

[WebSocket RFC 6455](https://www.rfc-editor.org/rfc/rfc6455) defines
bidirectional framing over a connection; [TLS 1.3 RFC
8446](https://www.rfc-editor.org/rfc/rfc8446) defines transport security
mechanisms. Neither proves FleetForge authorization, expiry behavior or resource
bounds. Test real sessions, wrong peers, disconnects, expiry, slow consumers and
reconnect pressure in the owning slices. Revisit only for demonstrated
topology/operational need with updated contracts and backlog.
