# Understanding agent release examples

An agent release updates the FleetForge service on a device. The
[workload release walkthrough](releases-explained.md) describes applications that
service manages. Agent replacement needs its own approval, compatibility checks
and independent recovery owner: Bootstrap.

The schemas and fixed examples exist today. Publishing agent bundles, accepting
activation instructions and replacing the installed agent still need implementation.
Use this guide to read the examples; the [specification](../specs/agent-releases.md)
owns exact validation rules.

## Read a fixture

Open [vectors.json](../../examples/agent-releases/conformance/v1/vectors.json).
It contains four cases: an artifact and an activation instruction for each intended
Linux architecture. Each case's `document` is the JSON object that its named
`schema` validates. The surrounding fields are expected answers for development
tests; they are not part of a published document.

Start with `artifact-linux-64`. Its document describes a prebuilt agent environment:

| Example field                                                 | What it tells the reader                                        |
| ------------------------------------------------------------- | --------------------------------------------------------------- |
| `release_id: agent-0.1.0-linux-64`                            | The immutable agent release identity                            |
| `package`                                                     | The agent package's name, version and build inside the archive  |
| `archive`                                                     | The expected SHA-256 and byte size of the archive               |
| `platform: linux-64`, `rust_target: x86_64-unknown-linux-gnu` | The target CPU/package combination                              |
| `os_profile`                                                  | Which locally approved OS compatibility profile must match      |
| `bundle`, `bootstrap`                                         | Which unpacker and Bootstrap versions may handle it             |
| `agent_schema`                                                | Which database schema versions the candidate can read and write |
| `security_policy_epoch: 1`                                    | The security policy level this artifact satisfies               |
| `signing`                                                     | The publisher key ID and signature algorithm                    |

These profile and tool versions are illustrative. They do not establish supported
runtime versions. The archive hash identifies fixture text, not a real bundle.
The ARM64 example changes the platform/target pair; it is format evidence only.

Next read `activation-linux-64`. It binds the artifact's metadata digest to one
`device_id`, `authority_id` and `assignment_id`. Its `generation: 2` orders agent
activation requests for that assignment/device. Its minimum security policy epoch
prevents an authorized rollback from selecting software below the required policy.
A lower display version can be selected by a new generation only if current
trust, schema compatibility and security policy allow it.

## Apply the schemas to the right objects

Validate an artifact's `document` against
[artifact.schema.json](../../schemas/agent-releases/v1/artifact.schema.json), and
an activation's `document` against
[activation.schema.json](../../schemas/agent-releases/v1/activation.schema.json).
For example, an unknown field or an AMD64 platform paired with an ARM64 Rust
target fails structural validation. Passing the entire vector wrapper to either
schema also fails: the wrapper contains test expectations, not artifact fields.

The separate [signature schema](../../schemas/agent-releases/v1/signature.schema.json)
validates an envelope containing `schema_version`, `document_digest` and
`signature`. Each vector supplies the last two values as expected answers.
A future publisher emits that envelope beside the canonical document.

Schema validation establishes structure. It cannot establish that an archive
exists, its bytes match, its publisher is trusted, or the device authorized a
particular activation. It also cannot compare schema/version range endpoints or
consult the device's durable generation counter. Those require semantic checks
by the future reader.

## Follow bytes through approval and activation

The fixture's `canonical_utf8_hex` is the exact signed document encoded as hex.
`document_digest` hashes those bytes. `signature_message_hex` adds the document's
signature domain and a NUL separator before those bytes. `public_key` and
`signature` let tests verify that exact message.

The publisher signs an agent artifact. A separately trusted activation authority
signs the instruction selecting it for a device. Each uses a different signature
domain and trust store, so publisher approval alone cannot order an installation.
The fixture uses a public test key; it must never become operational trust.

For contributors, run the fixed conformance checks from the repository root:

```sh
pixi run --locked -e host python -B -m pytest tools/agent_releases/test_agent_contracts.py
```

The checks verify schema structure, exact bytes and signatures, including rejection
under the wrong signature domain. They exercise no installation or recovery.
See the [fixture notes](../../examples/agent-releases/conformance/v1/README.md)
for key provenance and [maintenance handoff](../architecture/agent-delivery.md#exclusive-maintenance-and-replacement)
for the planned replacement sequence.
