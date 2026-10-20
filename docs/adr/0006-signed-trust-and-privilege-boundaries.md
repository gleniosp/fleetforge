# ADR 0006 — Signed trust and workload privilege boundaries

- **Status:** Accepted MVP security boundary; implementation pending.
- **Date:** 2026-10-20
- **Delivery:** [M1-06](https://github.com/gleniosp/fleetforge/issues/86),
  [M2-05](https://github.com/gleniosp/fleetforge/issues/87),
  [M4-08](https://github.com/gleniosp/fleetforge/issues/89).

## Context

“Trusted local” cannot make an arbitrary CA-issued peer a deployment writer or
prevent a managed workload from rewriting its own trust policy. Hashes detect
byte changes but do not establish who approved a release. Transport
authentication alone does not bind a stored/replayed instruction to its intended
assignment.

## Decision

Require unique device credentials, mutual peer authentication plus registry
scope authorization, local operator authentication and separate OS user/file
privileges for workloads. Use established libraries for detached Ed25519
publisher signatures over immutable release descriptors and separate authority
signatures over versioned immutable instructions. Publisher private keys stay
off devices; setup generates disposable secrets rather than committing them.

The [initial threat model](../architecture/security.md) owns trust boundaries,
required bindings, key/session lifecycle and rejection behavior. Exact encodings
and key IDs are specified by the release/protocol slices before implementation.
Essential authentication, authorization, signing and privilege controls are
mandatory MVP work. FUT-06 owns production lifecycle and hardening.

## Alternatives and consequences

Hashes alone permit unauthorized replacement; CA trust alone lacks assignment
permission; transport-only trust does not authenticate durable instruction
bytes. One shared secret/key collapses publisher, authority and device powers.
Separate roles and signatures make provenance and scope explicit but require
provisioning, keyrings, expiry/replacement procedures and negative tests from
the first slices.

Manual local provisioning avoids introducing a production enrollment service.
Offline revocation is not instantaneous. Accepted local work remains autonomous
subject to trusted inputs/resources. These controls do not establish production
security, host-root containment or physical robot safety.

## Sources, evidence and revisit conditions

[Ed25519 RFC 8032](https://www.rfc-editor.org/rfc/rfc8032) specifies the
signature scheme; use maintained libraries rather than implementing
cryptography. Future [TUF
metadata](https://theupdateframework.io/docs/metadata/) lifecycle hardening is
separate from an initial local keyring. No executable security boundary is
validated by this ADR. Require tamper/wrong-key/cross-assignment/expiry/CSRF
tests and real workload-permission checks. Revisit manual lifecycle for
production or shared untrusted deployment while preserving role separation and
durable payload trust.
