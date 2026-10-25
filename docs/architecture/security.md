# Initial threat model and trust boundaries

**Status:** Required MVP design; controls and negative tests are not
implemented. [ADR 0006](../adr/0006-signed-trust-and-privilege-boundaries.md)
explains this boundary. Production hardening remains
[FUT-06](future.md#fut-06--production-security).

## Assets, actors and assumptions

Protect device identity, assignment/authority policy, credential/key material,
accepted intent, active/known-good release inputs, recovery metadata,
observations and operator sessions. Setup manually provisions a local CA, public
keyrings, registry bindings and disposable test credentials in a controlled
development installation. One configured tenant does not remove
ownership/authorization checks.

The local CA/provisioner, trusted publisher and authorized deployment authority
have distinct powers. The publisher approves immutable software; the authority
chooses an authorized release for an assignment; a transport credential proves a
peer binding. Neither a valid CA chain nor knowledge of an identifier grants all
three powers. A compromised authority signing key can authorize deployments
within its scope; a compromised publisher can endorse harmful software. Key
custody and workload isolation remain necessary even when signatures verify.

## Threats and required controls

| Threat / boundary crossed | MVP response and required evidence |
| --- | --- |
| Network interception, impersonation or unauthorized CA-issued peer | TLS 1.3 mutual TLS, hostname/peer verification, unique device credentials and registry authorization; wrong CA/identity/assignment rejects |
| Cross-tenant/device/assignment or wrong-authority instruction | Verify exact registry scope and authority-signed payload bindings before acceptance; negative field-by-field tests |
| Tampered/unsigned release or descriptor substitution | Trusted publisher signature plus content digests verified before preparation/activation; reject unknown key, unsupported encoding and altered bytes |
| Replay, conflicting intent or stale authority restore | Durable request/generation semantics and restore quarantine from the [coordination contract](coordination.md); no automatic takeover/replay |
| Expired credentials or long-lived sessions | Block new authorizations and terminate or revalidate at expiry; test expiry during live sessions and disconnected execution |
| Compromised managed workload | Separate OS user/permissions; workload cannot read agent keys or modify SQLite, policy or trusted release inputs; real permission tests |
| Malicious paths, descriptor argv or symlinks | Validate owned roots, traversal, symlink/ownership and platform/version rules; explicit argv, no arbitrary remote shell |
| Unauthenticated browser write, cross-site request or session theft | Manually provisioned local operator authentication, protected sessions, same-origin/CSRF checks and bounded requests; no unauthenticated network control API/UI |
| Oversized traffic, slow peer, reconnect storm, stdout or disk exhaustion | Finite capacity/deadlines, fair queues and reserved recovery space; reject overload before durable acceptance and test retained control progress |
| Secret/history exposure through logs or observations | Bounded security decision codes without secrets, authorized reads and source context; historical tenant/assignment privacy |

Network attacks and compromised workloads are in scope for these controls. A
privileged host/CA compromise, physical tampering, kernel escape and physical
robot safety are not solved by the MVP. The reference setup must document its
real privileges, exposed listeners and filesystem boundaries before claiming
isolation.

## Signed inputs

Use detached Ed25519 signatures through established libraries. Publisher and
authority signing keys are separate from each other and from transport
identities. Publisher private keys never go to devices; setup generates test
secrets and keeps them out of repository source and logs. Devices receive
trusted public publisher and authority key bindings, local CA material and
unique transport credentials.

Publisher signatures cover versioned immutable release descriptor bytes,
including execution-relevant file/manifest/lock digests and
platform/entrypoint/health context. Authority signatures cover versioned
immutable instruction bytes bound to protocol version,
tenant/asset/device/assignment/authority, generation, request ID, release ID and
descriptor digest. A valid signature cannot override registry authorization.
Deduplication compares immutable payload semantics rather than signature or
framing representation. Hashes prove byte integrity, not trusted provenance or
download permission.

The [release specification](../specs/releases.md#canonical-bytes-and-detached-signature)
owns exact publisher-signed bytes, domain/version separation, key IDs, local
keyring replacement and review fixtures. [M4-01
(#25)](https://github.com/gleniosp/fleetforge/issues/25) must specify the separate
instruction encoding before implementation. These are design contracts;
executable signature verification still requires its owning delivery. Check
signatures and integrity before preparation and activation, including recovery inputs; unsafe or untrusted
inputs fail closed with an actionable decision record.

## Local privileges and key lifecycle

Run workloads without agent privileges. Protect agent SQLite, identity/policy,
private keys, public trust policy and immutable trusted inputs with explicit OS
user/file ownership. Validate runtime/cache/state paths and prevent workload
output from consuming critical recovery capacity. Do not give managed workloads
arbitrary agent credentials, host control or a remote-shell channel.

Use local trusted keyrings and manual rotation/replacement initially; record
expiry and replacement procedures with fixture provisioning. Credential rotation
preserves device identity. Network expiry blocks new authorization and
terminates/revalidates sessions while already accepted work remains local under
its input/resource trust checks. Revocation cannot be instantaneous for an
offline device. Automated production enrollment, revocation services, protected
publisher signing and TUF-style trust/metadata lifecycle are future hardening,
not excuses to omit MVP verification. See [TUF
metadata](https://theupdateframework.io/docs/metadata/) for that future
trust-lifecycle context.

Keep bounded local security decision records with actor/assignment/correlation,
decision codes and timestamps without secret material. These records are not an
enterprise compliance audit service or an indefinite retention guarantee.

## Delivery and evidence

Release trust will be implemented by [M1-06
(#86)](https://github.com/gleniosp/fleetforge/issues/86), agent
credentials/privileges by [M2-05
(#87)](https://github.com/gleniosp/fleetforge/issues/87), transport
authorization by [M4-07
(#88)](https://github.com/gleniosp/fleetforge/issues/88), instruction signing by
[M4-08 (#89)](https://github.com/gleniosp/fleetforge/issues/89), and protected
API reads/writes by [#29](https://github.com/gleniosp/fleetforge/issues/29) and
[#91](https://github.com/gleniosp/fleetforge/issues/91). Each slice includes
relevant rejection and real boundary tests. Production IAM, security-service
availability, incident response and independent review remain future
requirements; no production-security claim follows from this design.
