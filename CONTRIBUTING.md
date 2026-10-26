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

Issue forms and PRs are public reporting surfaces when the repository is public;
repository visibility is not a substitute for a private reporting channel.
Remove tokens, passwords, private keys, personal data, and private fleet or
network details from reports, logs, screenshots, archives, and Git history.
Use synthetic examples where possible. Follow [SECURITY.md](SECURITY.md) for
suspected vulnerabilities, including accidental credential exposure, before
posting technical details. The [code of conduct](CODE_OF_CONDUCT.md) covers
participation and conduct concerns.

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

The browser sign-in flow above does not require a personal access token. If you
choose a fine-grained token, scope it to the selected repository and operations,
set an expiration, and supply it through `GH_TOKEN` as described in the
[CLI environment reference](https://cli.github.com/manual/gh_help_environment).
A fork-scoped token grants no upstream write access or review bypass. Check
GitHub's current [token limitations and setup](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
and [operation permissions](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens)
before choosing scopes; some external-contributor operations require the web
interface or normal `gh auth login` flow.

## Development setup

Follow the [development guide](docs/guides/development.md) to install the locked
Pixi/Cargo contributor toolchain for your host and build the agent bootstrap
diagnostic. Contributor-host support and managed-device runtime support are
separate; the guide records prerequisites and validation limits.

Before handing off document/configuration changes, run the canonical
[formatting and check commands](docs/guides/development.md#repository-formatting)
and review the diff. Pre-commit may apply formatter fixes and stop the commit;
review and restage those fixes before retrying.

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

## PR checks and maintainer review

Every PR targeting `main` runs **PR checks / Repository checks**, including
documentation-only PRs. The [development guide](docs/guides/development.md#pr-checks)
explains the checks, revision selection and local reproduction; the linked
workflow owns CI configuration.
Inspect failures in the Actions step logs.
For fork PRs, a maintainer may need to approve the workflow run first.

Recommended `main` rules are to require a PR, require the **Repository checks**
status check from GitHub Actions, require the branch to be up to date, and
require maintainer review of the final diff. Configure approving-review counts
for the available maintainers; GitHub prevents authors from approving their
own PRs. The working agreement's local review and maintainer-controlled merge
still apply to a sole maintainer's own PR. Dismiss stale approvals when the
reviewed code changes. These are recommendations for maintainer configuration;
the workflow does not change repository rules or enable auto-merge.

A green check establishes automated validation, not approval of scope,
provenance, security claims or milestone completion. Maintainers review those
and decide whether to merge under the
[working agreement](docs/working-agreement.md#review-commits-and-publication).

## Evidence and permissions

Use [ADR 0003](docs/adr/0003-bounded-decisions-and-evidence.md) for bounded
technical questions and distinguish accepted design from observed behavior.
The [experiment-evidence skill](.agents/skills/experiment-evidence/SKILL.md)
helps structure those records. Consult the agreement's
[permissions and upstream policy](docs/working-agreement.md#permissions-and-upstream-collaboration)
before external or privileged actions.

## Licensing and provenance

Submit only material you have the right to contribute. Contributions intended
for inclusion in FleetForge are under the project's
[Apache-2.0 license](LICENSE), unless explicitly stated otherwise and accepted
by the maintainer; see section 5 of that license. Preserve third-party terms and
attribution rather than presenting external work as original project work.
Follow [THIRD_PARTY.md](THIRD_PARTY.md) for source, dependency, image, and release
input provenance and the information reviewers need. Flag uncertain permissions
before asking for inclusion.

## Project decisions and conduct

The repository maintainer, [gleniosp](https://github.com/gleniosp), decides issue
scope, contribution acceptance, and project policy. The
[working agreement](docs/working-agreement.md) owns the delivery and review
process. Ordinary technical or policy questions belong in a focused issue or
PR; explain the reason for a proposed change and allow others to disagree
respectfully. Maintainers should explain material decisions in the relevant
discussion without exposing private reports.

The [code of conduct](CODE_OF_CONDUCT.md) owns conduct expectations, reporting,
and the limits of the provisional enforcement process. The
[security policy](SECURITY.md) owns vulnerability reporting and current support
limits. These policies may be refined as the project and maintainer capacity
grow; they do not promise a staffed reporting service.
