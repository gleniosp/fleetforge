# Repository tools

Run these Python modules from the repository root through the locked host
environment. [Task reference](../docs/guides/tasks.md) lists the supported commands;
[development](../docs/guides/development.md) owns setup and validation.

## Release tooling

`releases/catalog.py` implements workload catalog integrity checks and provisioning;
`releases/trust.py` implements publisher verification and disposable signing.
The [provisioning guide](../docs/guides/release-provisioning.md) explains their use.
Tests live beside these modules and consume the shared [schemas](../schemas/README.md)
and [examples](../examples/README.md).

## Agent release contracts

`agent_releases/test_agent_contracts.py` checks agent artifact and activation
schemas, canonical bytes and signatures using fixed vectors. The
[agent release walkthrough](../docs/guides/agent-releases-explained.md) explains
the examples and validation boundaries.

## Shared JSON encoding

`json_encoding.py` supplies canonical encoding for the integer-only JSON domain
used by both release formats. It owns no artifact-specific trust or error policy;
the workload catalog translates numeric encoding failures into its release errors.
