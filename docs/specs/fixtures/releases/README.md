# Release contract review fixtures

These are illustrative inputs for the [version 1 release contract](../../releases.md),
not installable ROS releases or trusted publisher signatures. #11 owns actual
workloads/locks and #86 owns generated signing fixtures and cryptographic tests.

| File                                                               | Purpose                                                                                                     |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| [release-a.json](release-a.json), [release-b.json](release-b.json) | Readable descriptor objects for distinct release IDs and intended ROS behavior                              |
| [payloads.json](payloads.json)                                     | Exact illustrative UTF-8 file contents indexed by label and path; escaped `\n` becomes one LF byte          |
| [vectors.json](vectors.json)                                       | Canonical descriptor bytes, descriptor digests and domain-separated signature message bytes, encoded as hex |
| [catalog.json](catalog.json)                                       | Protected local locator entries for those ID/digest pairs                                                   |
| [keyring.json](keyring.json)                                       | Public key from RFC 8032 section 7.1 test 1, labelled for shape review only                                 |
| [signature-shape.json](signature-shape.json)                       | Structurally valid envelope with deliberately invalid all-zero signature                                    |

The readable descriptor JSON files include whitespace/final LF for source review.
They are **not** canonical on-disk `release.json` inputs. Decode the respective
`canonical_utf8_hex` vector to obtain the required exact bytes. Both descriptors
use ASCII strings and integer numbers, so sorted compact JSON produces the same
bytes as JCS for these specific objects; it is not a general JCS implementation.
The readable JSON files may be pretty-printed without changing the decoded
objects, payload strings or canonical hex vectors. They are included in the
repository formatter. This does not permit formatting actual canonical release
inputs, whose exact bytes participate in digests/signatures.
The vectors contain no signature or private key. The public RFC test key must
never be provisioned as an operational trust root.

Schema validation establishes shape only. In particular, `signature-shape.json`
must pass its schema and must fail cryptographic verification. The payload
texts are comments/placeholders, and manifest/lock consistency must fail if they
are passed to an actual release checker. That deliberate limit avoids claiming
ROS/package compatibility before #11. No fixture should be installed/executed.

## Review matrix

Apply each mutation independently to the stated base. For stages after signature
verification, assume #86's correctly signed equivalent so an earlier invalid
signature does not hide the intended fault. For a semantic unsupported value,
classify `release_unsupported` before reporting the generic schema failure.

| Base / change                                                                                                                 | Expected result and stage                                                                        |
| ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| A and B objects, files and vectors unchanged                                                                                  | Shape/hash/canonical-vector agreement; IDs, digests and expected behavior differ                 |
| Pretty descriptor file used directly as `release.json`                                                                        | `release_invalid`, canonical byte comparison                                                     |
| Reorder object members or append LF to canonical bytes                                                                        | `release_invalid`, canonical byte comparison; no silent reserialization                          |
| Duplicate `release_id` JSON member                                                                                            | `release_invalid`, strict parse before schema/canonicalization                                   |
| Set descriptor `schema_version` to 2                                                                                          | `release_unsupported`, version dispatch                                                          |
| Set `platform` to `linux-aarch64`                                                                                             | `release_unsupported`, device target dispatch                                                    |
| Set `signing.algorithm` to `Ed25519ph`                                                                                        | `release_unsupported`, algorithm dispatch                                                        |
| Add an unknown descriptor field                                                                                               | `release_invalid`, schema                                                                        |
| Set an application path to `../escape`, `/tmp/x`, `app//x`, `app/./x`, `app/../x`, `C:\\x`, `app\\x`, `%2e%2e/x` or append LF | `release_invalid`, schema/path rules                                                             |
| Duplicate a file entry or put a file beneath another file's path                                                              | `release_invalid`, semantic path-set validation                                                  |
| Replace a payload/parent with a symlink, hard link or special file                                                            | `release_invalid`, safe filesystem inspection before reading payload                             |
| Leave catalog/request digest unchanged and alter descriptor behavior                                                          | `release_integrity`, computed descriptor digest comparison                                       |
| Recompute digests after altering behavior but retain old signature                                                            | `release_untrusted_publisher`, signature verification                                            |
| Change a payload byte without changing descriptor                                                                             | `release_integrity`, file hash/size check after valid signature                                  |
| Add an unlisted payload file                                                                                                  | `release_integrity`, exact file-set check                                                        |
| Remove a listed payload file                                                                                                  | `release_unavailable`, required input inspection                                                 |
| Omit `release.sig.json`                                                                                                       | `release_untrusted_publisher`, required signature                                                |
| Empty keyring or absent `example-publisher-1`                                                                                 | `release_untrusted_publisher`, local trust lookup                                                |
| Keep key ID but substitute another valid public key                                                                           | `release_untrusted_publisher`, cryptographic verification                                        |
| Use all-zero signature from shape fixture                                                                                     | `release_untrusted_publisher`, cryptographic verification                                        |
| Substitute B's signature envelope for A                                                                                       | `release_integrity`, envelope digest comparison; changing its digest alone still fails signature |
| Repeat an ID in catalog or bind A ID to B digest against retained A binding                                                   | `release_conflict`, catalog/durable binding validation                                           |
| Same ID/digest/files provisioned again                                                                                        | Idempotent; does not alter the immutable binding                                                 |
| Catalog directory missing or request unknown ID                                                                               | `release_unavailable`, lookup/open                                                               |
| Descriptor larger than 1 MiB or payload sum over 4 GiB                                                                        | `release_invalid`, bounded read/aggregate limit                                                  |
| Probe timeout larger than startup timeout                                                                                     | `release_invalid`, semantic health bounds                                                        |
| Nonce/instance/digest from previous workload; correct probe exit code                                                         | `release_unhealthy`, current attempt comparison                                                  |
| Correct identities but wrong observed ROS behavior/inactive lifecycle                                                         | `release_unhealthy`, actual probe/behavior verification                                          |
| Correct local inputs, missing cached package bytes under network isolation                                                    | `release_prepare_failed`, installation; actual proof belongs to #14                              |

Review outcomes and reproducible shape/vector checks are recorded in the
[delivery journal](../../../journal/2026-10-24-release-contract.md). This matrix
defines required expectations, not a report that runtime rejection tests passed.
