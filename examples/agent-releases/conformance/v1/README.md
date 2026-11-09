# Agent contract vectors, version 1

These are illustrative metadata, not installable bundles or operational platform
claims. The [specification](../../../../docs/specs/agent-releases.md) owns the
contract. `vectors.json` contains artifact and activation examples for each
intended Linux architecture, their exact canonical UTF-8 bytes (hex), SHA-256,
domain-separated signature message, public key and Ed25519 signature.

Signatures use the public RFC 8032 test key (test vector 1), solely as reproducible
public fixture material. The public key is
`d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a`.
Never provision this key as trusted operational policy. Separate fixture key IDs
illustrate separate trust roles; production policy must provision them separately.
The archive digest refers to ASCII `fixture archive; not an installable bundle`.
Format/unpacker versions and OS profile names are illustrative, not selected values.

The [walkthrough](../../../../docs/guides/agent-releases-explained.md) explains
how to apply schemas to these documents and read the expected answers.

Run `pixi run --locked -e host python -B -m pytest tools/agent_releases/test_agent_contracts.py`.
The tests consume fixed expected answers rather than regenerate them, verify
signatures and reject alternate workload/agent domains, modified bytes, missing
bindings and unknown fields. They do not enforce runtime trust, replay, schema
migration or safe extraction; those remain the failure-table obligations in the
specification and future runtime deliveries.
