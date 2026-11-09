# Agent artifacts and activation, version 1

**Status:** Accepted contract for #147; schemas and conformance vectors exist.
No Bootstrap, helper, agent updater or activation reader is implemented.
[Agent delivery](../architecture/agent-delivery.md) owns lifecycle and recovery.
Workload [release v1](releases.md) remains a separate, compatible contract.

## Documents and canonical bytes

The [artifact](../../schemas/agent-releases/v1/artifact.schema.json),
[activation](../../schemas/agent-releases/v1/activation.schema.json) and
[signature](../../schemas/agent-releases/v1/signature.schema.json) schemas use
Draft 2020-12, reject unknown fields at every level, and are authoritative shared
inputs for future readers. Resolve them locally; never fetch schemas during
verification. Builders must embed these sources when distributing a reader.

An artifact describes one immutable agent environment archive. `release_id`
binds permanently to one metadata digest; a conflicting digest rejects.
`version` is a display/compatibility version, while `package.name`,
`package.version` and `package.build` identify the prebuilt agent Conda package
inside the bundle. Archive `digest` is SHA-256 of exact archive bytes and `size`
is their byte count. Package identity must match inspected bundle contents;
metadata alone cannot establish this. No source build runs on the device.

`platform` is a Conda subdir, paired exactly with `rust_target`:
`linux-64` with `x86_64-unknown-linux-gnu`, or `linux-aarch64` with
`aarch64-unknown-linux-gnu`. `os_profile` names a protected local compatibility
profile, including OS, ABI/libc and required system capabilities. Unknown
profiles reject. #69 establishes measured profiles; a conformance fixture's
profile is illustrative and grants no runtime support.

`bundle.format` is `pixi-pack`; `format_version` identifies the bundle format
contract, and `unpacker_version` the exact approved unpacker implementation.
Future #145 must establish actual supported values; fixture versions are examples.
Readers require an explicit local supported tuple, never assume that equal
major versions imply archive compatibility. `bootstrap.minimum` and `maximum`
are inclusive supported Bootstrap versions. All version fields use exactly three
nonnegative decimal components, with no leading zero, prerelease or build suffix.
Compare components numerically, never lexically; minimum must not exceed maximum.

`agent_schema.read` and `.write` each declare an inclusive integer range.
Minimum must not exceed maximum. Bootstrap checks the actual database schema
against both candidate read/write ranges before starting it, and checks any
proposed migration target against the retained recovery agent's read/write ranges.
An agent may write only its declared schema range. Migration planning must name
the target schema before mutation. If recovery compatibility cannot be retained,
reject activation until an explicitly authorized recovery/migration procedure
exists. Never reset identity or restore an old DB merely to fit an older binary.

Use RFC 8785 JCS, UTF-8 without BOM or final newline, for both signed documents.
Reject duplicate members, invalid Unicode, floats, noncanonical encoding and
unknown fields. Integers are at most 2^53−1. Strings in these formats are ASCII.
A document digest is `sha256:` followed by lowercase SHA-256 of canonical bytes.
The detached envelope is ordinary strict JSON using the signature schema;
`document_digest` must equal the computed digest.

Pure Ed25519 signs exactly one of these messages (the separator is one NUL byte):

```text
ASCII("FleetForge.agent-release.v1") || 0x00 || canonical_artifact_bytes
ASCII("FleetForge.agent-activation.v1") || 0x00 || canonical_activation_bytes
```

Use established RFC 8032 implementations. The signed `signing.key_id` selects a
protected local key binding with algorithm Ed25519 and a 32-byte public key.
Publisher, activation-authority and workload-publisher trust stores are separate;
an identical key ID grants no cross-store permission. No document can supply its
own trusted public key. The signature is 64 raw bytes encoded as 128 lowercase
hex characters. Never try another domain, algorithm or trust store on failure.

## Activation authorization and replay

A publisher signature approves artifact bytes, not installation on any device.
A separate signed `agent-activation` document binds `device_id`, `authority_id`
and `assignment_id` to `release_id` and `artifact_digest`. The helper checks
these against locally provisioned device/assignment and activation-authority
policy, independently of the requesting manager. IDs use existing canonical ULIDs.
Hardware replacement or assignment change requires trusted reprovisioning and
explicit replay-state handoff; it cannot reset the counter implicitly.

`generation` increases in a separate agent-activation sequence for this
assignment/device, independent of workload generations and semantic version.
The protected Bootstrap journal binds each accepted generation to its full
instruction digest. An exact retry returns its recorded outcome; equal generation
with other bytes or any lower generation rejects. Persist acceptance and the
new high-water mark atomically before side effects. Serialize concurrent acceptance.
An unavailable, corrupt or missing journal after provisioning fails closed.

`minimum_security_policy_epoch` may only increase the protected local floor.
The artifact's `security_policy_epoch` must meet the maximum of the current
floor and the instruction floor. Commit the floor with acceptance and never
lower it during recovery. A requested rollback is a new higher generation
pointing to retained compatible metadata; lower semantic version is permitted
only when schema, current trust and security policy still allow it. Automatic
recovery is a recorded substep of the accepted transaction, not replay of an old
instruction. Recheck the recovery artifact against the newly committed floor
before admission so acceptance cannot destroy the only permitted recovery path.

## Verification and bounded staging

Before stopping the current agent: bound and parse metadata, validate schema and
canonical encoding, verify activation trust/scope/replay, verify publisher trust
and requested artifact digest, check platform/profile/tool versions and schema
compatibility, then verify archive size/digest and inspect its complete contents.
Reject a missing independently runnable Bootstrap/recovery agent before admission.
Acceptance occurs only after these preflights and maintenance admission; recheck
policy and replay state under the serialized admission lock before committing.
No unpacker, package hook or candidate code runs before artifact verification.

Version 1 budgets are 64 KiB per signed document, 4 KiB per envelope, depth 8,
4 GiB archive bytes, 16 GiB expanded bytes and 100,000 archive entries.
These are conservative input budgets, not measured device capacity. Reserve disk
for staging and retained recovery before admission; fail without deleting recovery
inputs when capacity is insufficient. Reads, extraction and readiness need local
finite deadlines owned by the runtime delivery; exceeding them is a failed attempt.

Inspect both outer archive and nested package members. Reject absolute paths,
`..`, empty or dot components, backslashes, drive prefixes, NUL, duplicate names,
file/directory collisions, symlinks, hard links and special files in transport
archives. Use ASCII relative paths up to 240 characters with segments matching
`[A-Za-z0-9_][A-Za-z0-9._-]*`; reject rather than normalize. Prevent traversal and
replacement races with owned handles and a fresh protected staging root. An
unpacker that cannot enforce these rules is unsupported. Package-generated links
inside a reconstructed environment need separately validated containment policy
in #145; they do not relax archive input checks. Published archive bytes cannot
be rewritten to satisfy these rules under the same digest.

## Conformance and failure review

[Fixed vectors](../../examples/agent-releases/conformance/v1/README.md) bind exact
canonical bytes, digests, signature messages and public signatures. Schema tests
cover both target pairs, required metadata and unknown fields. The following
semantic cases are required of future runtime readers; schema/signature checks
alone do not implement them.

| Case                                                                             | Required decision before agent stop        |
| -------------------------------------------------------------------------------- | ------------------------------------------ |
| Workload signature used for agent artifact, or artifact signature for activation | Reject domain/trust mismatch               |
| Unknown metadata/version/profile or mismatched target pair                       | Reject unsupported input                   |
| Hostile archive path/link, digest or size mismatch                               | Reject staging; preserve current/recovery  |
| Lower generation, conflicting retry, lower security epoch                        | Reject replay/policy downgrade             |
| Candidate cannot read/write current schema, recovery cannot use migration target | Reject incompatible migration              |
| Missing Bootstrap or recovery environment                                        | Reject admission                           |
| Valid older version under new generation and current policy                      | Permit preflight; readiness still required |
