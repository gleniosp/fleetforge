# ADR 0003 — Bounded decisions and evidence

- **Status:** Accepted engineering policy.
- **Date:** 2026-10-19
- **Updated:** 2026-10-20

## Context

The design includes firm product boundaries and implementation details still
needing validation. Treating a plausible design, compiling code, or a UI status
label as a verified deployment would hide operational failure. Open-ended
investigation of future technologies would delay the current dependency-aware
slice.

## Decision

Before relying on tool behavior or generating technical configuration, consult
its current stable official documentation. For an important uncertainty:

1. State one concrete question and why the active milestone needs it.
2. Identify a small viable set of approaches, including the proposed default.
3. Consult official documentation; record version-sensitive assumptions.
4. Run a minimal experiment where documentation is insufficient.
5. Record setup, commands, inputs, versions, observations, and failure evidence.
6. Recommend a decision, including limits and revisit conditions.
7. Update the owning ADR/specification, implementation/tests, and GitHub scope.

Introduce checks and diagnostics with each capability. Tests must assert actual
behavior: workload response/identity, environment path, persisted
intent/generation, phase events, and observed outcome as appropriate. Use real
process integration for supervision/deployment; use deterministic faults and
explicit barriers. Filesystem or database labels alone do not prove successful
execution.

Record implementation and evidence independently from accepted design. The
journal records what ran and its limitations; GitHub owns live
progress/checklists. A review-ready task includes complete implementation,
relevant validation, documentation, and decisions in one deliverable. Do not add
future research, infrastructure, packages, or no-op tasks as hidden
prerequisites.

## Alternatives and consequences

An exhaustive technology survey might explore more options but has no useful
stop condition for bootstrap. Deferring tests/observability until the final demo
would make early lifecycle failures difficult to explain. The bounded approach
supplies decisions when needed and keeps evidence close to the behavior it
verifies.

Every evidence report states what was not tested. Failed experiments may
invalidate a proposed implementation default; they do not automatically justify
expanding MVP scope. Material contract changes require maintainer direction and
coordinated documentation, GitHub planning, and verification updates.

## Review triggers

Revisit the process if investigations repeatedly cannot answer the stated
question, evidence is irreproducible, or the current gate omits a demonstrated
failure domain. The [delivery and upstream
policy](../README.md#delivery-boundary) owns issue/PR sizing, authorized
upstream collaboration and workaround handoffs. Changes should improve concrete
decision quality rather than impose artificial deadlines or speculative release
requirements.
