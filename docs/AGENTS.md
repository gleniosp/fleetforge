# Documentation guidance

Inherit [root agent guidance](../AGENTS.md). Use the
[documentation map](README.md) to find each authoritative owner and the
[working agreement](working-agreement.md) for scope and delivery policy.

- Edit the owning requirements, architecture contract, or ADR and update its
  affected references and traceability together. Keep navigation pages brief.
- Keep the [glossary](product/glossary.md) up to date when documentation introduces
  or changes shared terms and actor responsibilities. Reuse existing definitions,
  add concise entries for new concepts, and link to their owning contracts or
  explanatory guides rather than duplicating detailed rules.
- Write concise, natural prose that explains what the reader needs to do and
  why. Explain purpose, main commands and non-obvious constraints; link to code
  and configuration instead of restating settings or task definitions. Keep
  agent writing instructions in the applicable `AGENTS.md`, not reader guides.
- Follow the documentation map's current-state rule: keep revision narratives
  and factual historical evidence in journals or experiment reports. Keep ADR
  rationale relevant to the current decision. Preserve historical evidence; add
  a dated correction when necessary.
- Distinguish accepted design, implemented behavior, and verified behavior using
  the map's [evidence definitions](README.md#reading-design-and-evidence).
- Use [ADR 0003](adr/0003-bounded-decisions-and-evidence.md) and the
  [experiment-evidence skill](../.agents/skills/experiment-evidence/SKILL.md)
  when a real uncertainty needs investigation. Routine link/diff checks belong
  in delivery evidence and do not require a new experiment or ADR.
- Check relative file links and fragments, requirement references, fenced blocks,
  final newlines, and diff whitespace. Review Mermaid source and disclose when
  rendered layout was not inspected. Match GitHub links and task mappings to live
  scope when changing planning references.
