# Repository formatting — 2026-10-26

## Inputs and tools

Delivery for [#132](https://github.com/gleniosp/fleetforge/issues/132), on
`build/132-editorconfig-formatting-checks`, in the working tree based on
`06dd4706f26e43102279c5719438f061edbdac3d`. The branch began clean.
[ADR 0007](../adr/0007-repository-formatting.md) owns the configuration and hook
decision; this journal records one-off delivery validation. No permanent
formatter-specific test suite or extra Python dependency is introduced.

Local platform: Linux x86_64. Host-installed Pixi 0.83.0 matches the repository
minimum. The lock resolves dprint 0.63.0 from the explicit
`https://prefix.dev/github-releases` channel for linux-64, linux-aarch64 and
osx-arm64, adding one package per environment/platform without changing existing
package resolutions. No Node/npm dependency was added. The separate Oxc Wasm
plugin is 0.47.0, with SHA-256
`531f729b3ebf18203a07b9c2da869eef5003130ac6a8936c2eca28cf6ee8b20b`.
Its committed URL includes that checksum. The native package declares no
additional dependencies. Latest upstream dprint was 0.64.3; 0.63.0 was available
on the selected channel for all three supported native hosts.

Reviewed official dprint configuration/CLI/plugin/editor documentation, Prek
configuration and Pixi's manifest reference. Checked used flags/protocol against
dprint 0.63.0, hooks against Prek 0.5.7, and channel/task syntax against Pixi
0.83.0. Official sources are linked in ADR 0007. Bare channel names resolve under
anaconda.org, so shortening this channel to `github-releases` changes its source.

## Direct checks and migration

```sh
pixi install --locked -e host
pixi run --locked -e host setup
pixi run --locked -e host fix
pixi run --locked -e host check
pixi run --locked -e host prek run --all-files --stage pre-commit --skip fix
git diff --check
```

Locked installation, plugin preparation and hook configuration validation passed.
The final host `check` directly composes `format-check` and `hooks-validate`,
without invoking the hook runner. `fix` composes `format`. Snapshot comparison
confirmed a second fix pass was idempotent, the check preserved source bytes,
and neither command changed `pixi.lock` or `Cargo.lock`.

One-off migration comparison used locally available Python 3.14.4,
markdown-it-py 3.0.0 and PyYAML 6.0.3, without adding project dependencies.
Rendered Markdown structure/text was compared while normalizing ordinary prose
whitespace and preserving literal code/comments. All 49 Markdown documents,
15 JSON documents, five TOML and five YAML files retained their parsed meaning
through the initial formatting pass. Manual review covered the full diff,
tables, hard breaks, frozen examples and configuration/task ownership.
Mermaid source was preserved; rendered interactive diagram layout was not checked.

Removing the blanket release-fixture exclusion then allowed layout changes in
the readable descriptors. All seven fixture JSON files were compared before and
after formatting using `json.loads(..., object_pairs_hook=list)`: decoded values,
member order, payload strings and canonical hex vectors were identical. These
objects are source-review containers, not the actual canonical `release.json`
bytes. The fixture README explains that distinction. Repeated schema/vector
validation uses the preserved command in the
[release-contract journal](2026-10-24-release-contract.md): five schemas, five
fixture documents, both A/B vectors and 24 schema mutations passed, including
payload hashes and canonical descriptor/signature-message vectors.

Markdown link/fragment review passed across all 49 files. A pre-existing journal
link targeted the task guide's missing feature/environment heading; restored
that heading at its owning explanation. The release-contract progressive
examples and diagram/prose numbering were also checked: six JSON examples,
five diagrams and 26 corresponding numbered actions agreed.

## One-off editor and hook validation

Representative unformatted Markdown, JSON, JSONC, YAML and hidden TOML failed
read-only checks, then formatted and passed. UTF-8, LF/final newline, meaningful
Markdown hard breaks and frozen JSON fences were checked. Invalid JSON failed
without source repair. Generated/lock files and unowned Python were rejected by
formatter selection. EditorConfig's explicit fallback allowlist excluded the
dedicated document/code formats.

The actual schema-5 editor service from the executable selected in VS Code
settings produced the same bytes as CLI formatting for all five representative
formats with the pinned project configuration/plugin. The protocol client closed
stdin after shutdown acknowledgement for clean termination. Interactive VS Code
activation and debugger UI were not exercised.

The final repository-wide hook was exercised using `git init` in a disposable
checkout containing the delivery manifest/lock, formatter, hook configuration,
Commitizen configuration, LICENSE and actual Git attributes/ignores. Ran host
`setup`, committed a baseline, then used installed hooks through `git commit`:

- Staged `sample.json` containing `{"value":1}` and untracked `draft.json`
  containing `{"draft":true}`. Pre-commit formatted both, failed for modified
  staged content and preserved the original index bytes. Explicit restaging
  followed by a Conventional Commit message passed.
- Staged already formatted `{"value":2}`, then changed only the working tree to
  unformatted `{"value":3}`. The commit passed and restored the exact unstaged
  bytes afterwards.
- Staged unformatted `{"value":4}`, then changed the same line to
  `{"value":5}` without staging. Formatter fixes conflicted with restoration;
  Prek failed, rolled back the fix and preserved both index and working-tree
  versions.

Prek's untracked-only changes may not fail a commit; the repository-wide hook
intentionally reaches those drafts. No fixture operation staged or committed
anything in the delivery checkout. Earlier one-off staged-hook validation also
confirmed refusal of unstaged hook-configuration edits and successful
commit-message checks. Those checks do not establish interactive editor behavior.

## Runtime and host evidence

The existing device checks were run during this delivery:

```sh
pixi run --locked -e device device-check
pixi run --locked -e device device-test
pixi run --locked -e device device-build
```

Formatting/Clippy, all ten existing CLI tests and the build passed. Subsequent
host hook/task simplification changed no Rust source or Cargo configuration.

The clean Ubuntu walkthrough was run with fresh environments/caches, the pinned
Ubuntu base and mounted host Pixi. It passed fresh installs, isolated tool paths,
builds, lock rejection, inherited unsafe lint and source preservation, plus
formatter setup/checks. Observed host: Ubuntu 24.04.5 LTS, glibc 2.39,
ca-certificates `20260816ubuntu0.24.04.1`, Pixi 0.83.0. Linux dprint is static PIE
with no GLIBC symbol-version requirements, so it does not raise the documented
glibc floor. The later hook simplification was validated locally as above; the
walkthrough no longer carries a formatter integration harness. Its current
reproduction entry point is [verify.sh](../../experiments/pixi-toolchain/verify.sh).

Native ARM64 Linux, Apple Silicon macOS and WSL-specific integration were not
executed locally. The existing native CI matrix runs direct host checks and
commit-safety built-ins without fixes. Resolution is not native execution proof.
No managed-device runtime, ROS workload, cryptographic signing or artifact
transfer capability is claimed by this contributor-tooling delivery.

## Canonical descriptor protection

Added `**/release.json` to dprint exclusions and the matching Git attribute
`-text`, following the filename already defined by the release contract. No
standalone canonical descriptor file exists in the current inventory; readable
`release-a.json`/`release-b.json` fixtures remain formatter-owned. This guards
bytes without claiming canonical encoding validation or covering unknown future
exact-byte formats.

One-off validation copied the actual dprint configuration and Git attributes
into a disposable directory. Root and nested `release.json` containing
`{"z":2,"a":1}` remained byte-identical through normal formatting and explicit
path formatting, while the same contents in `release-a.json` were formatted.
In a disposable Git repository with `core.autocrlf=true`, `git check-attr text`
reported `unset` for both descriptor paths, and staging a CRLF byte sentinel
preserved its bytes in the index. That sentinel tests conversion protection,
not valid canonical encoding. Host `format`, `check`, relative link checks and
`git diff --check` passed after these changes.

The explicit `node_modules` exclusion remains unnecessary: dprint excludes those
directories by default. EOF fixing remains covered by dprint for its formats and
rustfmt for Rust. Fallback EditorConfig guides editor saves; no CLI EOF check is
claimed for plain text, shell or miscellaneous fallback files.
