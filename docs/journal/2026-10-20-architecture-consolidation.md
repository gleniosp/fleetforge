# Architecture consolidation evidence — 2026-10-20

**Task:** [M0-10 / issue #85](https://github.com/gleniosp/fleetforge/issues/85)

## Scope and baseline

Consolidated the issue's approved decision register into requirements,
architecture, ADRs, roadmap and traceability. The starting revision was
`192cde3` on the maintainer-created `docs/85-consolidate-architecture` branch.
GitHub issue #1 was already closed and remains historical initial publication.
The original [foundation journal](2026-10-19-foundation-design.md) is preserved
unchanged.

The current contracts include asset/device identity and first-schema ownership,
local durable authority/offline semantics, direct mutual TLS WebSocket push,
signed releases/instructions, workload privileges and real ROS 2 Jazzy releases.
Focused architecture documents own identity, coordination, security and future
constraints. ADRs 0001/0002 are explicitly amended, 0004–0006 record the
additional identity/transport/trust decisions, and 0003 retains the bounded
evidence policy.

The documentation map retains delivery-policy ownership, adds the maintainer's
`<type>/<issue-number>-<short-description>` branch convention and normally one
PR per issue, and records coherent combined-issue handling. It also owns focused
issue sizing and specifically authorized upstream collaboration/handoff policy.
The full working agreement and templates remain issue #2 work.

## Validation method

Use an authenticated GitHub CLI snapshot of all issues and milestones to compare
repository references and requirement mappings. Parse Markdown links/headings
with the available `markdown_it` package and Python standard library; check
local files and GitHub-style fragments, stable requirement IDs, fenced blocks,
final newlines and whitespace. Temporary review helpers/snapshots live under
`/tmp`; they are not project tooling or a supported contributor workflow.

Review the complete diff against issue #85's decision register, including every
MVP/FUT boundary and added issue #86–#114. Inspect diagrams as source and
identify superseded assumptions explicitly. Read primary ULID, WebSocket,
Ed25519, Pixi, RoboStack, ROS platform and TUF references for design context;
these are not runtime compatibility evidence.

## Initial review results

`python3 /tmp/fleetforge-doc-check.py` passed using the available Markdown parser
and standard library. It checked 19 Markdown documents and 448 links: 109 local
file/fragment links and 325 FleetForge GitHub links, with the remaining 14 external
references parsed. All referenced FleetForge issues/milestones existed in the
114-issue/21-milestone authenticated snapshot. Every issue was mapped in traceability;
per-issue MVP/FUT assignments matched the snapshot, including all added #86–#114
slices. All eleven MVP, twelve FUT and seven NFR IDs remained present.

The check inspected five fenced blocks, including four Mermaid source blocks,
final newlines and trailing whitespace, with no reported errors. `git diff --check`
passed. The old journal's bytes matched the starting revision. The native GitHub
blocker endpoint reported zero blockers for #85. External reference parsing is
not an exhaustive availability check of every third-party URL.

Manual decision-register review covered the following contracts:

| Register subject | Owning documentation and review result |
| --- | --- |
| Execution/Pixi ownership | Overview and ADR 0001 distinguish install/lock from authorization, activation, supervision and recovery |
| Identity/ownership | Identity contract and ADR 0004 specify canonical typed IDs, assignment context, replacement/clones and historical privacy |
| Authority/offline/restore | Coordination and amended ADR 0002 cover durable acceptance, retry/conflict/supersession, expiry and stale-ledger quarantine |
| Transport/bounds/freshness | Coordination and ADR 0005 select authenticated push with fair bounded work and source-aware projections |
| Trust/privileges | Security threat table and ADR 0006 require signatures, registry checks, local operator auth and workload separation |
| Real robotics | Requirements/overview require ROS 2 Jazzy A/B, isolated actual health and reproduced package gaps |
| Deferred capabilities/scale | Future architecture and traceability cover FUT-01–12, including fenced rollout/authority transfer, tenant-aware central restore and measured scale |
| Delivery/upstream | Documentation map owns branch naming, focused issue/PR sizing, authorized upstream work and maintainer-only approval/merge |

When publication is authorized, the PR will identify its final source revision;
no self-referential commit ID is invented inside this journal. Checklist completion
must cover only evidenced documentation work. Issue closure remains the PR's merge action.

## Maintainer workflow clarification

The maintainer specified local review before commits and PR publication. Updated
`docs/README.md` with the full sequence: request the next issue/branch, implement
and validate, local review, commit-message text on request, optional multiple
focused commits, then push/create a PR only when asked. The maintainer reviews
and merges the PR; the next task starts when requested after merge. A raise-PR
request authorizes pushing reviewed commits and creating the PR together; a
commit-message request does not run a commit.

At the maintainer's explicit request, updated GitHub issue #2's title, scope and
temporary delivery baseline to match that workflow and plan repository
`task-delivery`, `pull-request` and `experiment-evidence` skills. A search of the
114-issue backlog found no existing reusable experiment-skill owner; individual
experiments remain with their delivery issues. All #2 implementation criteria
remain unchecked. Skill implementation stays in #2, after the #85 baseline.
These local documentation changes remain uncommitted for maintainer review.

## Current-contract documentation review

The maintainer requested that authoritative contracts describe the present design
without narrating how issues or earlier proposals caused revisions. Removed
amendment/previous-proposal explanations from the ADRs and ADR index, the initial
publication exception from the delivery guide, and historical publication/backlog
narratives from the roadmap and traceability introduction. Retained decision
rationale, alternatives, consequences, useful delivery mappings and status/date
metadata. ADRs 0001–0003 carry a separate update date where relevant. The
documentation map now states this ownership rule for future edits.

The earlier entries in this journal preserve the sequence of design and review
work. Operational history/privacy and recovery requirements remain product
contracts; they are unrelated to document edit history.

Re-ran `python3 /tmp/fleetforge-doc-check.py` and `git diff --check` after the
cleanup. Both passed. The current set contains 19 Markdown documents and 438
links, including 108 local file/fragment links and 316 FleetForge GitHub links.
All 114 issues, 21 milestones and 30 requirement IDs remain covered; the four
Mermaid source blocks remain present. The original foundation journal remains
unchanged. This follow-up remains local and uncommitted for review.

## Evidence limits

This delivery changes documentation only. No product runtime, ROS/package
install, cryptographic verification, TLS session, OS permission boundary, crash
recovery, offline install or resource/scale experiment ran. No production or
million-device capacity claim is validated. Exact signed encodings, key IDs and
finite limits remain specified deliverables of the linked implementation slices.
Diagram source inspection does not establish GitHub-rendered layout.
