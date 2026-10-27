# 2026-10-27 — Python editor integration

Local evidence for [M1-08 (#137)](https://github.com/gleniosp/fleetforge/issues/137).
Source: uncommitted working tree on `build/137-python-ruff-vscode`, based on
`d73eed4c7bc737c1126b2308f1ca56a32b6b9a51`. Execution: Linux x86_64,
Python 3.14.10 and Ruff 0.17.3 from the existing host environment.

The [development guide](../guides/development.md#editor-integration) owns setup.
The recommendations add Python, Pylance and Ruff. Settings select the host
interpreter and Ruff executable, prefer filesystem policy and disable Ruff
fix-all/import organization on save. Existing document/Rust settings remain.
No dependency, lockfile or release payload changes are required.

Settings were reviewed against the official
[Python settings reference](https://code.visualstudio.com/docs/python/settings-reference),
[Ruff settings](https://docs.astral.sh/ruff/editors/settings/) and
[Ruff editor features](https://docs.astral.sh/ruff/editors/features/).
The configured executable paths exist locally; their version commands return
the versions above. Pylance does not replace the repository's strict mypy check.

## Bounded formatting check

Question: does the pinned Ruff language server preserve the existing release
formatting exclusions when a document is explicitly formatted? Prefer the
existing project policy if it works; editor exclusions would be needed only
if the server failed to honor that policy. Stop after checking mutable source
and both release paths. No additional infrastructure or dependencies are needed.

An initial CLI stdin probe unexpectedly formatted release-named input despite
the format exclusion. Reproduce with:

```sh
printf 'value=  1\n' | .pixi/envs/host/bin/ruff format --stdin-filename releases/ros-counter-a-v1/app/main.py
```

It returns `value = 1`, so that CLI path cannot establish editor behavior.
A direct LSP probe then launched `.pixi/envs/host/bin/ruff server`, using JSON-RPC
messages framed with `Content-Length` headers over stdin/stdout. Reproduce the
protocol sequence below, replacing workspace/document URIs with absolute file
URIs for the checkout:

1. Request `initialize` with `processId: null`, `rootUri` set to the checkout,
   `capabilities: {}`, `workspaceFolders: [{"uri": <checkout URI>, "name": "fleetforge"}]`
   and `initializationOptions: {"settings": {"configurationPreference": "filesystemFirst"}}`.
2. After the response, notify `initialized` with `{}`.
3. For each path below, notify `textDocument/didOpen` with
   `textDocument: {"uri": <document URI>, "languageId": "python", "version": 1, "text": "value=  1\n"}`.
4. Request `textDocument/formatting` with `textDocument: {"uri": <document URI>}`
   and `options: {"tabSize": 4, "insertSpaces": true}`; inspect its response,
   then notify `textDocument/didClose` with the same document URI.

| Document path                             | Formatting result                |
| ----------------------------------------- | -------------------------------- |
| `examples/ros-workloads/_editor_probe.py` | One edit producing `value = 1\n` |
| `releases/ros-counter-a-v1/app/main.py`   | `null`, no edits                 |
| `releases/ros-counter-b-v1/app/main.py`   | `null`, no edits                 |

Documents were opened only in server memory; no probe or payload was written.
The server honors the repository format exclusion, so no editor-specific
exclusion is necessary. Lint fixes remain separate from formatting and are
disabled on save. Revisit if Ruff changes exclusion behavior.

## Repository validation and limits

- `pixi run --locked -e host format`: passed.
- `pixi run --locked -e host check`: passed, including dprint, Prek configuration,
  Python formatting/lint and all three strict mypy scopes.
- `git diff --check`: passed; the full change was manually reviewed.

The first sandboxed check could not write the normal dprint/Prek caches;
the authorized rerun with normal cache access passed. No toolchain or runtime
changes require fresh-environment or ROS execution for this editor-only slice.
VS Code extension installation, UI activation, interpreter selection and
native ARM64/macOS execution were not tested. The direct language-server check
verifies formatting behavior independently of the VS Code UI.
