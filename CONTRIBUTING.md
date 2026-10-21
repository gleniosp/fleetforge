# Contributing to FleetForge

FleetForge is in early development. Read the [project overview](README.md) and
[roadmap](docs/roadmap.md) for current scope. Reports, proposals, documentation,
and focused implementation contributions are welcome; maintainers validate issues
and decide whether a proposed change belongs in the project.

## Report a problem or propose a change

Search [existing issues](https://github.com/gleniosp/fleetforge/issues) first.
If the problem or idea is new, open an issue in this repository using the
[issue chooser](https://github.com/gleniosp/fleetforge/issues/new/choose).
Use the bug report form for an observable failure, the proposal form for a
feature or improvement, or the delivery task form for a focused planned slice.

Describe the problem, expected result, and relevant context. For defects, include
a minimal reproduction, source revision, relevant commands/tool versions, and
sanitized output when available. Maintainers assess validity, scope, priority,
and dependencies and may request more information. Contributors do not need to
assign internal task IDs, requirement IDs, milestones, or priority labels.

Discuss substantial changes before investing in implementation. You can also
open a linked draft or exploratory PR to help validate the issue and demonstrate
an approach while that discussion is ongoing. Maintainers evaluate both the
issue and the proposed change; opening either does not guarantee acceptance.

## Submit a pull request from your fork

1. Fork [FleetForge](https://github.com/gleniosp/fleetforge) and create a focused
   branch in your fork. Follow the
   [branch and issue-sizing conventions](docs/working-agreement.md#branches-and-issue-sizing)
   once the change has an issue number.
2. Implement the change with its essential checks, configuration, documentation,
   and evidence. Use focused Conventional Commits under the
   [commit convention](docs/working-agreement.md#review-commits-and-publication).
3. Open a PR from your fork's branch into **`gleniosp/fleetforge:main`** using the
   PR template. Link the issue with `Refs #N` for a proposal or validation aid;
   use `Closes #N` when the PR completely delivers the issue. Mark incomplete or
   exploratory work as a draft and explain what remains.
4. Describe the change, actual validation results, and limits in the PR and link
   owning repository evidence. Respond to review feedback and update the PR.
   Maintainers decide whether the issue and PR are valid and whether to approve
   and merge the change into `main`. A draft PR can help that decision before
   implementation scope is accepted.

Contributors manage commits and PR submissions in their own forks. The
[working agreement](docs/working-agreement.md) owns the repository maintainer's
agent-assisted local review and publication workflow, GitHub state, and milestone
exit rules. Agent users should read [AGENTS.md](AGENTS.md); the repository skills
cover issue delivery, PR work, and bounded experiments. The
[documentation map](docs/README.md) identifies authoritative contracts.

## GitHub CLI (optional)

GitHub's web interface supports the complete issue and fork/PR workflow.
If you prefer the command line, install [GitHub CLI](https://github.com/cli/cli#installation)
globally in your own environment. FleetForge does not install, pin, or manage
`gh` as a repository dependency. Authenticate separately:

```sh
gh auth login
gh auth status
gh issue list --repo gleniosp/fleetforge
gh issue view ISSUE_NUMBER --repo gleniosp/fleetforge
```

After pushing your branch to your fork, you can submit it with:

```sh
gh pr create --repo gleniosp/fleetforge --base main --head YOUR_USER:YOUR_BRANCH
```

Replace the uppercase placeholders with your issue number, GitHub username, and
branch. Use `--draft` for exploratory or incomplete PRs. See the official
[authentication](https://cli.github.com/manual/gh_auth_login) and
[PR creation](https://cli.github.com/manual/gh_pr_create) documentation for options.
Keep credentials in your user environment and out of repository files and reports.

### Optional fine-grained personal access token

The browser sign-in flow above does not require you to create a personal access
token. If you choose a fine-grained token, GitHub CLI recommends supplying it
through `GH_TOKEN`; this takes precedence over saved credentials. See the
[CLI environment reference](https://cli.github.com/manual/gh_help_environment).

Select the appropriate resource owner and only the repositories needed for your
operations: your fork for fork changes, or `gleniosp/fleetforge` for authorized
maintainer operations. Set an expiration and grant permissions by operation:

| Operation on a selected repository | Repository permission |
| --- | --- |
| Read repository metadata | Metadata: read (included automatically) |
| Read source / push source changes over HTTPS with this token | Contents: read / read and write |
| Read / create or update issues | Issues: read / read and write |
| Read / create or update pull requests | Pull requests: read / read and write |
| Read workflow runs and logs, when needed | Actions: read |
| Push changes to workflow files, when needed | Workflows: read and write, in addition to Contents: read and write |

Choose only the rows and access levels you need. These permissions do not grant
repository membership or bypass maintainer review. A fork-scoped token does not
grant write access to upstream issues or PRs. GitHub currently limits fine-grained
tokens for public repositories where you are not a member and for outside or
repository collaborators; use GitHub's web interface or the normal `gh auth login`
flow for unsupported contribution paths. Check the current
[token limitations and setup guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
and [permission reference](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens)
for the operation you intend to perform.

## Development setup

Follow the [development guide](docs/guides/development.md) to install the locked
Linux x86_64 Pixi/Cargo toolchain and build the agent bootstrap diagnostic.

For documentation changes, inspect links and heading fragments, current contract
consistency, and the diff; follow [docs/AGENTS.md](docs/AGENTS.md). Use available
tools and record their actual commands and limits. Temporary review helpers do
not become supported project tooling merely because a journal mentions them.

## Commit messages

Follow the [commit-writing convention](docs/working-agreement.md#review-commits-and-publication);
for example, `build(hooks): validate commit messages`. Install the local hooks
using the [development guide](docs/guides/development.md#local-hooks-and-commit-validation).
The [task reference](docs/guides/tasks.md#hooks-and-commit-messages) owns manual
message/history checks, checker exemptions and staged-content behavior.

## Evidence and permissions

Use [ADR 0003](docs/adr/0003-bounded-decisions-and-evidence.md) for bounded
technical questions and distinguish accepted design from observed behavior.
The [experiment-evidence skill](.agents/skills/experiment-evidence/SKILL.md)
helps structure those records. Consult the agreement's
[permissions and upstream policy](docs/working-agreement.md#permissions-and-upstream-collaboration)
before external or privileged actions.

Licensing, distribution provenance, and contributor safety policy are owned by
[#8](https://github.com/gleniosp/fleetforge/issues/8); this guide does not
establish a license grant or a vulnerability reporting service.
