---
name: experiment-evidence
description: Resolve a bounded FleetForge technical uncertainty or record and review reproducible experiment evidence for an active delivery.
---

# FleetForge experiment evidence

Read [ADR 0003](../../../docs/adr/0003-bounded-decisions-and-evidence.md) and the
agreement's [permissions and upstream policy](../../../docs/working-agreement.md#permissions-and-upstream-collaboration).
Use the [documentation map](../../../docs/README.md) to choose the evidence owner.

State one concrete question needed by the active issue, a hypothesis when useful,
and a small viable set of approaches including the proposed default. Consult
current stable official documentation and identify version-sensitive assumptions.
Define the smallest useful experiment and its stopping condition before running
it. Use existing fixtures or recorded experiments when they answer the question;
label a retrospective review clearly rather than imply a new run.

Record enough for a contributor to reproduce and assess the result:

- Question, issue/requirement context, alternatives, and success/failure signal.
- Setup, source revision/working-tree state, platform and tool versions, inputs,
  preconditions, exact commands, and relevant outputs or failure evidence.
- Observations/results, then interpretation, uncertainty, and what was not tested.
- Decision or recommendation, owning ADR/spec changes when needed, revisit
  condition, and next action. An inconclusive result is valid evidence.

Put focused experiments with their owning delivery; use a journal for factual
review/implementation records and an ADR for a significant decision's rationale.
Link existing owners instead of duplicating reports. Ordinary implementation
tests belong with that delivery's checks and do not automatically need a separate
experiment. Accepted design, recorded observations, and newly measured behavior
must remain distinguishable; compiling or inspecting metadata alone cannot prove
product execution.

Stop when the question is answered or the stated limit is reached. Update
affected contracts and authorized issue scope/checklists only as supported;
validation evidence belongs in the repository and PR, not issue comments.
Preserve failed results and limits. If an upstream gap remains, follow the
agreement's reproducer/handoff and workaround-owner rules within existing
authorization. Do not introduce future infrastructure as an experiment dependency.
