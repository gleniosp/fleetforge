# Immutable releases and local catalog, version 1

**Status:** Accepted design for [M1-01 (#10)](https://github.com/gleniosp/fleetforge/issues/10)
and [MVP-02](../product/requirements.md#mvp-02--reproducible-software-releases).
Schemas and illustrative fixtures exist; a release reader, actual ROS workloads,
integrity checker and signature verifier are subsequent deliveries. This contract
does not establish runtime or cryptographic verification evidence.

For an introduction to the terms, their purpose and the complete planned flow,
read [From approved software to a running robot](../guides/releases-explained.md).

## Documents and identity

The [descriptor schema](schemas/release.schema.json), [catalog schema](schemas/catalog.schema.json),
[signature schema](schemas/signature.schema.json) and [publisher keyring schema](schemas/keyring.schema.json)
use JSON Schema Draft 2020-12. The rules below also apply: structural validation
cannot check file bytes, uniqueness by ID/path, canonical encoding, trusted keys,
or running processes. Reject unknown fields rather than ignore execution context.

A release directory contains `release.json`, `release.sig.json`, `pixi.toml`,
`pixi.lock` and the application files enumerated by `files`. Directories may only
contain enumerated files and their parent directories. Metadata files are excluded
from `files` to avoid circular hashes. No generated environments, credentials,
keyrings, catalogs or writable application data belong in this directory.

`release_id` is a case-sensitive opaque ASCII identifier, 1–64 characters,
starting with a lowercase letter/digit and then lowercase letters/digits, `-`,
`_` or `.`. It is independent of asset/device IDs and has no ordering or trust
meaning. A and B are explanatory labels, not mutable aliases. A release ID binds
to exactly one descriptor digest for its lifetime across all catalogs. Changing
files, execution policy, signing key or any descriptor field requires a new ID.

The 64-character maximum bounds the name; it does not supply collision resistance
or a generation algorithm. Publishing tools must check existing bindings. A
future generated-ID convention or management UI may prevent naming mistakes,
but readers still reject conflicting ID/digest pairs. No global ID allocator or
automatic conflict-resolution service is defined here. Conflict handling cannot
silently replace the contents associated with an existing ID.

`files` includes `pixi.toml` and `pixi.lock` exactly once, plus every application
file, sorted by ascending ASCII path. Each entry carries a lowercase hexadecimal
SHA-256 digest of the exact file bytes and its byte size. `manifest` and `lock`
are fixed paths naming those same entries; there is no second hash to reconcile.
The descriptor digest is lowercase SHA-256 of canonical `release.json` bytes,
represented externally as `sha256:<64 hex characters>`. It is not a field inside
the descriptor. Desired instructions bind both release ID and descriptor digest.

Version 1 supports only `platform: linux-64`, `runtime.environment: default`,
and `runtime.minimum_pixi_version: 0.83.0`. Linux x86_64 with Ubuntu 24.04 is the
reference runtime. These fields do not certify host compatibility; package/system
requirements in the independently owned manifest/lock still have to match the
actual device. A schema version, platform or runtime adapter outside the supported
set rejects before installation. Contributor hosts retain their separate matrix.

`runtime.environment` selects an environment from this release's own `pixi.toml`
and lockfile, not the repository root workspace. `default` is the initial single
application runtime; it does not inherit the root `default`, `host` or `device`
tooling. A and B own separate runtime inputs and installed environments even
though each calls its environment `default`.

## Canonical bytes and detached signature

Use [RFC 8785 JCS](https://www.rfc-editor.org/rfc/rfc8785) to encode descriptors.
Use UTF-8 without BOM. Reject duplicate object members, invalid Unicode, trailing
whitespace or a final newline. A reader parses strictly, checks the schema, then
requires the stored bytes to equal their JCS serialization. It must not silently
repair noncanonical input. Member ordering is JCS ordering; `files` ordering is
an additional semantic constraint. All numbers are bounded integers. Do not
normalize strings or line endings before hashing files.

The descriptor's `signing` object contains exactly `algorithm: Ed25519` and
`key_id`. These fields participate in the digest and signature. The signature
message is the concatenation of the following bytes:

```text
ASCII("FleetForge.release.v1") || 0x00 || canonical_descriptor_bytes
```

Use pure Ed25519 from [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032), not
Ed25519ph or Ed25519ctx, with an established library. The separator is one NUL
byte, not the two printable characters `\0`. Hashing the descriptor does not
replace signing this message. `release.sig.json` contains `schema_version: 1`,
`descriptor_digest`, and `signature`, the 64 raw signature bytes encoded as 128
lowercase hex characters. Its digest must equal the computed descriptor digest.
One signature is supported. The envelope may use ordinary JSON whitespace;
duplicate members and unknown fields still reject. Never select an algorithm
from an unverified alternate envelope or fall back to another key.

Lookup the signed `key_id` in the locally provisioned publisher keyring. Each
entry binds a unique ID to `algorithm: Ed25519` and `public_key`, the 32 raw
public key bytes as 64 lowercase hex characters. A key ID is a local label, not
a public key URL, download instruction or proof of authorization. Duplicate IDs,
invalid library key encodings or unsupported algorithms reject the keyring;
an absent key or invalid signature rejects the release. No embedded descriptor
key can grant itself trust. Authority keys and transport credentials are separate.

The shared schema helper `hex_32_bytes` names the decoded size: each byte uses
two hexadecimal characters. Both public keys and SHA-256 file hashes therefore
use 64-character hex strings for 32 bytes; this helper name is not a release field.

Provision matching public publisher bindings on authority and devices through
trusted local setup; protect the keyring against workload writes. Keep private
publisher keys solely on the signing host and out of source, devices and logs.
Generate disposable fixture secrets in #86. Manual replacement first provisions
a new ID/public key on required readers, then publishes new release IDs signed
by it. Retain old public bindings and verified inputs while active/known-good
releases require them. Removal is an explicit local distrust decision: inventory
affected active/recovery releases and provision trusted replacements before
removing a key. Never bypass verification to recover. Loss of trust may prevent
restart/recovery; surface that failure rather than silently stop an already
running workload. Manual distrust takes effect when each device receives policy;
this format provides no automatic expiry, online revocation or global freshness.

## Local catalog and validation order

`catalog.json` is protected local configuration with `schema_version: 1` and a
`releases` array of `{release_id, descriptor_digest, directory}` entries. The
directory is relative to a separately configured, provisioner-owned release
root; it is never relative to an arbitrary catalog location or network URL.
Sort entries by release ID. Directory names do not imply identity. The catalog
is an index rather than a signed authorization grant; its contents must agree
with the requested ID/digest and the signed descriptor before use.

The MVP provisions release inputs and catalog entries through trusted setup
before deployment. Creating a release does not propagate it to robots; only
robots that need it require provisioning. An existing trusted publisher key can
verify additional releases without a keyring change. Future
[artifact delivery](../architecture/future.md#fut-03--artifact-delivery-and-caches)
owns remote transfer and must specify how verified local availability is
registered in the catalog; this contract does not implement that automation.

Reject duplicate release IDs within one catalog even when identical. Provisioning
an existing ID/digest/files is idempotent; rebinding that ID to a different digest
is `release_conflict`, even if both signatures are trusted. Do not resolve a
collision by last writer wins or by deleting an existing entry first. Preserve
the ID/digest binding in durable deployment records when inputs are removed;
the persistence slice owns its storage. Multiple directories must not alias one
release through symlinks or map different entries to the same directory.

Validate in this order, with finite reads and no install, activation, Pixi hook,
health probe or workload execution until every applicable check succeeds:

1. Validate the catalog and requested ID/digest, detect collisions, resolve the
   owned directory, and open metadata safely within the configured root.
2. Strictly parse the descriptor/envelope, validate schemas and canonical bytes,
   supported version/platform/runtime and computed/requested/catalog digests.
3. Resolve the local publisher key and verify the detached signature.
4. Validate the complete file set, safe paths, byte sizes and hashes, including
   manifest/lock entries. Check manifest/lock consistency and platform/environment
   selection with the integrity/preparation adapter. Never update source locks.
5. Only then prepare a separate environment. Before activation or recovery,
   recheck current trust and input integrity, or rely on an equally protected
   verified snapshot whose immutability is enforced by ownership.

If several faults exist, report the first failing stage. The actual checker
arrives in #13, signature enforcement in #86 and deployment preparation in #20.
Earlier unsigned workload demonstrations must not be presented as trusted
deployment paths.

## Paths, files and finite input bounds

Paths use `/` and ASCII segments matching `[A-Za-z0-9_][A-Za-z0-9._-]*`.
Reject absolute paths, empty segments, `.`/`..`, backslashes, drive prefixes,
URLs, percent escapes and control characters; `cwd` alone may be `.`. Do not
decode, expand variables or normalize a bad path into an accepted one. Paths are
case-sensitive and at most 240 characters. Reject duplicate paths and file/parent
collisions. `cwd` must be an existing directory inside the release workspace.

The 240-character bound is an initial version 1 input policy, not a measured
filesystem limit or a portability guarantee. A legitimate deeply nested payload
could exceed it and would currently reject. The configured root adds characters
to the actual filesystem path, so provisioning must also validate the resulting
path and individual components against the target filesystem. Revisit this bound
with representative release layouts and platform evidence before changing it;
path length does not replace traversal, link and ownership checks.

Release metadata and payloads must be regular files under owned roots. Reject
symlinks at every path component, hard-linked payloads, sockets, devices and
FIFOs. Use race-resistant traversal/handles; a string prefix or a one-time
`realpath` check is insufficient. Provisioner/agent ownership must prevent a
workload from replacing validated bytes or directory entries between validation
and use. Package-managed links inside the installed environment are a separate
Pixi resource; this ban describes release inputs, not all dependency internals.

| Input/resource        | Version 1 maximum                                               |
| --------------------- | --------------------------------------------------------------- |
| Descriptor            | 1 MiB                                                           |
| Signature envelope    | 4 KiB                                                           |
| Catalog / keyring     | 1 MiB each                                                      |
| Entries               | 1,024 releases; 64 publisher keys; 4,096 files per release      |
| Payload bytes         | 1 GiB per file, 4 GiB total per release                         |
| Entrypoint/probe argv | 32 items, 1,024 characters each, no NUL                         |
| Health probe stdout   | 4 KiB, one JSON object; stderr separately bounded by supervisor |

Reject limits before unbounded allocation; JSON nesting is at most 16 containers.
Aggregate byte, encoded document, ordering and cross-field bounds need semantic
checks beyond the schemas. These are release input limits, not a device disk
reservation or a dependency-cache size guarantee. Later resource owners must
budget environments/cache/output and preserve known-good recovery capacity.

The 1,024-entry maximum applies to one local catalog document, not global release
history, fleet size or simultaneous workloads. It is an initial finite-input
budget, not measured capacity. Reject an oversized catalog rather than silently
truncate entries or evict active/known-good inputs. Larger histories may require
a revised bounded index/retention design; no automatic catalog cleanup or paging
mechanism is implemented here. Preserve required recovery inputs and durable
ID/digest bindings when any later retention policy removes local entries.

## Entrypoint and ROS health

`entrypoint` has `argv` and `cwd`. `argv[0]` is a path relative to the selected
installed environment, such as `bin/python`; other elements are literal arguments.
`cwd` is relative to the verified release workspace. Spawn directly without a
shell, PATH search, interpolation or arguments supplied by remote instructions.
Python application/probe paths in the examples are relative to `cwd`. A trusted
publisher can approve executable code; signatures do not make that code safe.

The adapter prepares the selected environment and supplies the activation
environment needed by ROS without executing descriptor-provided shell text.
The #11 workload delivery must establish its Pixi/ROS activation and package
compatibility. Clear inherited injection variables (including Python path/home
overrides), supply a controlled environment and disable writes of Python bytecode
into release inputs. Mutable logs/data and Pixi outputs use separate paths.
Manifest activation/build code is trusted release code too: it may only run
after publisher/integrity verification in deployment paths.

Before each spawn the supervisor generates a fresh random 128-bit
`process_instance_id` (32 lowercase hex characters); it is never restored/reused
for a new process. Inject these exact environment variables into workload and
probe: `FLEETFORGE_RELEASE_ID`, `FLEETFORGE_DESCRIPTOR_DIGEST`,
`FLEETFORGE_PROCESS_INSTANCE_ID`, plus the configured `ROS_DOMAIN_ID`.
The device fixture allocates independent ROS domains and private endpoints for
each workload instance, including consecutive attempts on one device. Domain
allocation is local policy rather than a signed device-specific release field.
The supervisor checks actual child ownership/liveness separately from health.

`health.kind` is `ros2-probe-v1`; its `argv`/`cwd` follow the entrypoint rules.
For each invocation inject a fresh unpredictable 256-bit
`FLEETFORGE_HEALTH_NONCE` (64 lowercase hex characters). The probe must exchange
that nonce with the actual workload through a ROS service/message round trip,
verify active ROS lifecycle/behavior, and observe the workload's release,
descriptor and process-instance identity. Echoing the probe's environment alone,
a live PID or a static metadata file cannot satisfy health. The response must
come from the current owned workload endpoint, within the probe deadline.

On success the probe exits zero and writes exactly one JSON object to stdout
with fields `schema_version: 1`, `status: healthy`, `release_id`,
`descriptor_digest`, `process_instance_id`, `nonce`, and `observed_behavior`.
Unknown/duplicate fields reject. The supervisor compares all identity/challenge
fields to its current attempt and `observed_behavior` to signed
`health.expected_behavior` (1–128 printable ASCII characters). The A/B fixture
values `counter-step-1` and `counter-step-2` describe intended distinct ROS
behavior; #11 defines and demonstrates the concrete service/message checks.
An exit error, timeout, malformed/oversized response, wrong identity/challenge,
inactive lifecycle or wrong behavior fails the probe. A dishonest compromised
workload is outside this functional health guarantee.

`startup_timeout_ms` is 1–300,000, `probe_timeout_ms` is 1–30,000 and
`interval_ms` is 1–10,000; probe timeout and interval must not exceed startup
timeout. Use monotonic time. Retry only until the startup deadline; kill/reap a
timed-out probe and do not overlap probes. Cap each probe and retry wait at the
remaining startup budget. A successful probe plus live owned
child establishes initial verification. The lifecycle slice owns later monitoring,
shutdown/retry budgets, attempt outcome and verified recovery. A reboot or
recovery spawn requires new instance identity and actual health verification.

## Inputs, installed environments and offline preparation

Keep three resources distinct:

- Immutable release files and signed metadata identify approved software.
- Pre-provisioned dependency/package bytes enable a fresh install without public
  internet. A lockfile records resolution; it does not contain those bytes.
- A release-specific installed environment is generated mutable installation
  output, isolated from contributor tooling and active/known-good environments.

Prepare from a verified protected workspace copy so `.pixi` outputs do not mutate
the immutable release directory. Check copied inputs against signed hashes;
reject lock/manifest drift. Do not share writable environments across releases or
let workloads modify trusted workspace inputs. Retain A's trusted inputs and
required package bytes for recovery and explicit rollback after B succeeds.

Pixi owns resolution, locks and environment installation. FleetForge owns input
trust, catalog bindings, provisioning policy, supervision, health and recovery.
The [latest official install documentation](https://pixi.prefix.dev/latest/reference/cli/pixi/install/)
and locally inspected Pixi 0.83.0 help agree that `--locked` checks lock freshness
and `--offline` fails when cache data is absent. Use the locked contract; frozen
mode alone does not check manifest freshness. This is flag compatibility evidence,
not proof of offline ROS installation. #14 must establish exact cache provisioning,
commands and positive/missing-byte behavior under verified network isolation.
No package layout, cache completeness, relocatability or offline success is
assumed here. Future artifact transfer is owned by FUT-03.

## Error vocabulary and review fixtures

| Code                          | Condition                                                                             |
| ----------------------------- | ------------------------------------------------------------------------------------- |
| `release_unavailable`         | Unknown ID, missing catalog/directory/metadata/payload; include missing resource kind |
| `release_conflict`            | Duplicate/rebound ID or conflicting catalog/durable digest binding                    |
| `release_unsupported`         | Unsupported schema, platform, algorithm, runtime or health kind                       |
| `release_invalid`             | Malformed/noncanonical JSON, schema/limit/path/file-type violation                    |
| `release_integrity`           | Digest/hash/size mismatch, unexpected file or inconsistent manifest/lock              |
| `release_untrusted_publisher` | Missing signature, absent/unknown key, invalid public key or failed signature         |
| `release_prepare_failed`      | Verified inputs cannot install, including missing dependency bytes                    |
| `release_unhealthy`           | Actual workload/probe verification fails or times out                                 |

A missing signature uses `release_untrusted_publisher`, not generic missing-file
classification. An unsupported version/algorithm uses `release_unsupported`
even though it also fails a schema constant. Include stage, release ID/digest
when available and bounded safe resource context; omit secrets. Input/preparation
failure must preserve the active workload. These codes do not declare attempt
state or authorize a process stop.

The [fixture guide](fixtures/releases/README.md) supplies A/B descriptors, hashes,
catalog/keyring/envelope examples and a rejection matrix. Review it alongside
the schemas and semantic rules. Implementation deliveries must turn these
expectations into side-effect-aware runtime tests.
