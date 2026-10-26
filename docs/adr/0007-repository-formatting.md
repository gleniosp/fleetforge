# ADR 0007 — Centralized repository formatting

- **Status:** Accepted maintainer direction; implementation subject to local review.
- **Date:** 2026-10-26
- **Requirement:** [MVP-01](../product/requirements.md#mvp-01--engineering-foundation)
- **Delivery:** [#132](https://github.com/gleniosp/fleetforge/issues/132)

## Decision

Use dprint with one Oxc Wasm plugin for current Markdown, JSON/JSONC, YAML and
TOML. Pixi's lint feature pins the native executable from the explicitly selected
`github-releases` channel; [dprint.json](../../dprint.json) pins the plugin's
version and SHA-256. Setup prepares both inputs. The plugin runs inside dprint;
no Node/npm, separate Oxfmt or additional document formatter is required.

Keep format selection, exclusions and layout in that one configuration. Adopt
the pinned plugin's defaults unless a present requirement needs an override;
disable embedded-code formatting to preserve examples. Exclude generated data
and package-manager locks. Format readable release-fixture objects while
preserving their values, member order and embedded canonical hex/payload strings.
Exclude canonical `release.json` descriptors and disable Git text conversion for
that filename. Add protections for other exact-byte inputs with their owning
delivery; exclusions do not validate canonical encoding. Checks never repair
contractual bytes by reserializing them.

Rust retains device-scoped rustfmt/Clippy. Add Python, JavaScript/TypeScript or
other language tooling/configuration only when its owning code needs it.

EditorConfig is a fallback allowlist for files without a dedicated formatter,
including plain text, miscellaneous text configuration, shell and Docker inputs.
It does not set competing rules for dprint-owned formats or Rust/Python. dprint
does not read EditorConfig. Formatter output is consistent across editors and
CLI; typing indentation and file-encoding preferences remain editor behaviours.
There is no custom configuration generator or synchronization tool.

VS Code selects the locked dprint executable and uses the same project
configuration/plugin. Settings contain tool routing and save behaviour, without
duplicated whitespace/layout options. Recommend dprint, EditorConfig,
rust-analyzer and CodeLLDB, preserving the maintainer's optional Oxc
recommendation; editor installations remain optional.

## Task and hook boundaries

Define `format` and read-only `format-check` once in Pixi. Both support optional
paths and otherwise cover eligible working-tree files, including untracked
inputs. Host `check` directly composes `format-check` and hook-configuration
validation; host `fix` composes `format`. Add actual component lint checks/fixes
when needed. Device checks/tests remain separate.

Prek runs one repository-wide `fix` hook without filename arguments, the
Conventional Commit message hook and three non-formatting safety built-ins:
case conflicts, merge conflicts and large added files. Drop duplicate syntax
checks and generic whitespace rewriting. dprint parses its selected formats;
blanket whitespace fixes can alter meaningful literal text or canonical bytes.
Fallback EditorConfig remains editor guidance, not a CLI validator for all text.

Changes to tracked/staged files fail the hook for review and explicit restaging;
never stage fixes automatically. Prek snapshots/restores unstaged tracked edits
and rolls back fixes if restoration conflicts. Eligible untracked drafts remain
visible and may be formatted; those changes alone may not fail the hook.
CI runs direct host checks and the three safety hooks with `fix` skipped on each
supported native contributor platform. No permanent formatter test harness is
introduced; one-off integration and semantic validation belong in delivery evidence.

## Coverage and dependencies

| Present files                                                              | Owner                                                              |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Markdown, JSON/JSONC, YAML and TOML, including dot-directory configuration | dprint/Oxc                                                         |
| Readable release-fixture JSON                                              | dprint/Oxc; decoded canonical vectors and payload values preserved |
| Rust                                                                       | Existing device-scoped rustfmt/Clippy                              |
| Plain text, shell/Docker and miscellaneous text configuration              | Explicit EditorConfig fallback                                     |
| Dependency locks and generated output                                      | Manager-owned/excluded                                             |

dprint is the only new direct development dependency. Its channel packages
declare no package dependencies; Linux execution and prerequisites were checked.
Keep the explicit `https://prefix.dev/github-releases` channel URL: Pixi resolves
bare channel names under `anaconda.org`, which is a different location. The
existing native host matrix remains unchanged. Device development environments
retain their existing lint/test composition; managed-device runtime manifests do
not acquire contributor tooling.

## Rationale and revisit conditions

A native runner and one sandboxed Wasm plugin cover the current formats and
editor integration with one formatting configuration. Plugin distribution is
separate from Pixi, so its bytes require an explicit pin/checksum and setup cache.
Fallback-only EditorConfig avoids competing formatter rules while retaining
cross-editor conventions for otherwise unmanaged text.

Revisit if the plugin loses semantic fidelity, package/platform support changes,
new file types need an owner, or editor/CLI output diverges. Keep the tool set
proportionate to present files and preserve independent runtime boundaries.
The [delivery journal](../journal/2026-10-26-repository-formatting.md) owns actual
versions, reproducible validation and limitations.

## Official references

- [dprint configuration](https://dprint.dev/config/), [CLI](https://dprint.dev/cli/)
  and [Oxc plugin](https://github.com/dprint/dprint-plugin-oxc).
- [VS Code extension](https://github.com/dprint/dprint-vscode) and
  [editor-service protocol](https://github.com/dprint/dprint/blob/0.63.0/docs/editor-extension-development.md).
- [EditorConfig behaviour](https://editorconfig.org/) and
  [dprint's EditorConfig decision](https://github.com/dprint/dprint/issues/4).
- [Pixi manifest](https://pixi.prefix.dev/latest/reference/pixi_manifest/) and
  [0.83.0 reference](https://github.com/prefix-dev/pixi/blob/v0.83.0/docs/reference/pixi_manifest.md).
- [Prek configuration](https://prek.j178.dev/configuration/) and
  [0.5.7 stage reference](https://github.com/j178/prek/blob/v0.5.7/docs/reference/configuration.md).
