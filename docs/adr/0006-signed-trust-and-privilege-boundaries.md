# ADR 0006 — Signed trust and workload privilege boundaries

- **Status:** Accepted MVP security boundary; implementation pending.
- **Date:** 2026-10-20
- **Updated:** 2026-10-24
- **Release contract:** [M1-01](https://github.com/gleniosp/fleetforge/issues/10),
  [version 1 specification](../specs/releases.md).
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
required bindings, key/session lifecycle and rejection behavior. The
[release specification](../specs/releases.md) defines JCS canonical descriptor
bytes, SHA-256 descriptor identity, a versioned domain prefix and detached pure
Ed25519 signatures. Algorithm and publisher key ID are inside the signed
descriptor; a protected local keyring supplies the public key. Release IDs cannot
be rebound to new digests, including when replacing a signing key. Instruction
encoding remains with the protocol slice before implementation.
Essential authentication, authorization, signing and privilege controls are
mandatory MVP work. FUT-06 owns production lifecycle and hardening.

## Alternatives and consequences

Hashes alone permit unauthorized replacement; CA trust alone lacks assignment
permission; transport-only trust does not authenticate durable instruction
bytes. One shared secret/key collapses publisher, authority and device powers.
Separate roles and signatures make provenance and scope explicit but require
provisioning, keyrings, expiry/replacement procedures and negative tests from
the first slices.

Canonical JSON gives the Rust authority/agent and release tooling one exact
byte representation while keeping descriptors inspectable. Rejecting alternate
serializations makes digest equality explicit; it also requires a conforming
JCS serializer and strict duplicate-member handling. Detached signatures avoid
self-referential digests. A domain/version prefix prevents using release signing
messages as another FleetForge payload type. Signing algorithm/key ID prevents
unverified envelope metadata from changing their interpretation. Hashing exact
file bytes includes manifests, locks and executable application inputs.

Signing arbitrary serializer output would leave multiple byte identities for
the same object; embedding a descriptor digest in its own input is circular.
Mutable ID aliases would make rollback and durable intent ambiguous. Manual
keyring replacement is intentionally local and may require new releases to
preserve recovery trust; it does not provide automatic offline revocation.

Manual local provisioning avoids introducing a production enrollment service.
Offline revocation is not instantaneous. Accepted local work remains autonomous
subject to trusted inputs/resources. These controls do not establish production
security, host-root containment or physical robot safety.

## Sources, evidence and revisit conditions

[Ed25519 RFC 8032](https://www.rfc-editor.org/rfc/rfc8032) specifies the
signature scheme; [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) defines JCS.
The [contract fixtures](../specs/fixtures/releases/README.md) and
[design review journal](../journal/2026-10-24-release-contract.md) record schema,
byte-vector and manual rejection-case review, not signature verification.
Use maintained libraries rather than implementing
cryptography. Future [TUF
metadata](https://theupdateframework.io/docs/metadata/) lifecycle hardening is
separate from an initial local keyring. No executable security boundary is
validated by this ADR. Require tamper/wrong-key/cross-assignment/expiry/CSRF
tests and real workload-permission checks. Revisit manual lifecycle for
production or shared untrusted deployment while preserving role separation and
durable payload trust.
