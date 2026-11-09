# Independent agent lifecycle contracts

## Scope and inputs

Working tree for #147 based on `00031465100dbccca8cdf427a377c477530e3208`.
[ADR 0009](../adr/0009-pixi-agent-delivery.md),
[agent delivery](../architecture/agent-delivery.md) and
[artifact v1](../specs/agent-releases.md) adopt the independent Bootstrap contract, with native foundation evidence
before M2–M8 and a subsequent local VM recovery proof. No runtime updater or new package dependency is introduced.
Existing workload schemas, signed descriptors and payload bytes are unchanged.

The [official Pixi pack guide](https://pixi.prefix.dev/latest/deployment/pixi_pack/)
was read on 2026-11-09. It documents transport/reconstruction, not safe extraction,
FleetForge authorization or crash recovery. Project minimum Pixi is 0.83.0;
this host runs 0.84.1. This delivery invokes no pack/unpack command and makes no
compatibility claim; #145 must pin and validate a concrete tuple.

## Static evidence

Reproduce from repository root:

```sh
pixi run --locked -e host python -B -m pytest tools/releases/test_agent_contracts.py
pixi run --locked -e host python-check
pixi run --locked -e host format
pixi run --locked -e host check
```

Results: **9 conformance checks passed**; Python formatting, Ruff and strict mypy
passed. Repository format/check passed after allowing their required dprint/Prek
cache writes outside the workspace; the initial sandboxed attempt could not write
those caches. Diff whitespace and local documentation links were reviewed.

The Python environment is 3.14.10 with pytest 9.1.1. Fixed RFC 8032 fixture-key
signatures cover AMD64/ARM64 artifact metadata and their separate activation
instructions. Checks verify canonical encoding, digest/message bytes, public
signatures, cross-kind and modified-byte rejection, required/unknown fields and
unsupported artifact values. These are conformance checks, not an updater reader.

Manual contract review covered the specification's failure table and delivery
interruption table: cross-kind trust, hostile archive paths/links, stale generation,
policy floor during rollback, candidate/recovery schema compatibility, missing
recovery executable, pending maintenance handoff and journal interruption.
The handoff drains under the agent's lock before Bootstrap acquires it, while a
protected fence prevents new transitions. Failure leaves admission fenced until
the helper reconciles. No runtime or rendered diagram review is claimed.

## Limits

Native builds, ABI profiles, actual bundle versions, archive inspection, privilege
isolation, maintenance locking, schema migration and interruption recovery remain
unimplemented obligations for #69/#148/#145/#87/#17/#19 and the explicitly deferred
Bootstrap VM deliveries. The schemas enforce structure and target pairing; range
ordering, trust, anti-replay state and filesystem safety require future readers.
Contract acceptance does not expand the operational device/workload matrix.

## Package separation follow-up — 2026-11-09

Working tree based on `b5eca4bdd4ec6292213b85c074ddf2f09c9bd7a6` moves the agent conformance checks to
`tools/agent_releases/test_agent_contracts.py`. The earlier command above records
the original validation location; use the new path for current focused checks.
Both release formats now import canonical encoding from `tools/json_encoding.py`.
Workload parsing retains its classified numeric errors. Guide/example navigation
and `tools/README.md` describe the separate packages and shared encoding module.

`pixi run --locked -e host python -B -m pytest tools` passed **66 tests**, including
the moved vectors and shared encoding regressions for UTF-16 ordering, integer
bounds, floats, Unicode and workload error classification. Repository format/check,
Ruff and strict mypy passed. No installation or recovery behavior was exercised.
