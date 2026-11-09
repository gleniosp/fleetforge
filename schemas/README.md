# Machine-readable contracts

- [Release schemas, version 1](releases/v1/) — descriptors, catalogs, detached
  signatures, public publisher keyrings and their shared definitions.
- [Agent release schemas, version 1](agent-releases/v1/) — agent artifacts, activation instructions and detached signatures; [format rules](../docs/specs/agent-releases.md).

The [release specification](../docs/specs/releases.md) owns the accompanying
format rules. Publisher tooling and future agent builds consume or bundle these
schemas from this shared source. [Conformance fixtures](../examples/releases/conformance/v1/README.md)
provide fixed expected answers for implementation tests.
