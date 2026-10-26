# Task delivery guidance evidence — 2026-10-20

**Task:** [M0-02 / issue #2](https://github.com/gleniosp/fleetforge/issues/2)

## Scope and source

Initially implemented contributor/agent navigation, one owning working agreement, three
repository skills, two issue templates, and a PR template on the
maintainer-created `docs/2-maintainer-task-delivery` branch. This record describes
the uncommitted working tree based on
`dbbe2e09a1f8d88dcfe6d42a125bd565688f3ff7`.
The [working agreement](../working-agreement.md) owns workflow policy; the
documentation map's existing delivery/selection/upstream anchors now route to
it. Historical journals remain unchanged.

Consulted official [OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills)
for repository discovery and required frontmatter, and
[agent instruction documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
for scoped instruction discovery. Consulted GitHub's
[issue template guidance](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository)
and [PR template guidance](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository)
for file locations and metadata. Skills contain instructions and relative
references; they require no new runtime, plugin, script package, or user settings.

## Validation setup and method

Available review tools: Python 3.14.4, markdown-it-py 3.0.0, PyYAML 6.0.3,
Git 2.53.0, and GitHub CLI 2.98.0 on the current Linux host. These are inspection
tools, not a supported FleetForge toolchain or newly pinned project dependencies.
The skill-creator validator was read/run from the installed system skill at
`/home/gleniosp/.codex/skills/.system/skill-creator/scripts/quick_validate.py`.

Fetched an authenticated snapshot of all 114 issues and 21 milestones using
`gh issue list --repo gleniosp/fleetforge --state all --limit 200 --json number,title,state,labels,milestone,body,url`
and `gh api 'repos/gleniosp/fleetforge/milestones?state=all&per_page=100'`.
Inspected #2's native blockers, the local branch/history, the default branch,
and PR #115's merge information. #1 is closed historical initial publication;
#85 was delivered by [merged PR #115](https://github.com/gleniosp/fleetforge/pull/115)
at the base revision above. Its merge occurred on 2026-10-20. #2 is the earliest
unblocked P0 task in active M0 even though its discovery label remains backlog.

The temporary `/tmp/fleetforge-issue-2-check.py` review helper uses Git's tracked
and non-ignored untracked file inventory, parses Markdown after YAML frontmatter,
resolves relative file/heading links, checks issue/milestone references and
requirement-to-issue traceability, final newlines/whitespace, and Mermaid source.
It also compares historical journal bytes with the base revision. Temporary
helpers/snapshots are review artifacts, not committed contributor tooling.

Run the metadata validator for each final skill directory, then the document
check and Git whitespace check:

```sh
python3 /home/gleniosp/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/task-delivery
python3 /home/gleniosp/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/pull-request
python3 /home/gleniosp/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/experiment-evidence
python3 /tmp/fleetforge-issue-2-check.py
git diff --check
```

## Workflow walkthrough

Read the final skills and follow their references through the agreement for the
scenarios below. This is a manual policy walkthrough using the current Git/GitHub
state and clearly hypothetical publication cases. It is not an independent agent
run or an execution of GitHub mutations.

| Request/state examined                                               | Result of applying the skill and agreement                                                                                                                                                                 |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Find next work in the live snapshot                                  | Task-delivery selects #2 by active milestone, P0 priority, stable ID and delivered #1/#85 prerequisites, despite the backlog label and milestone text still referring to #85 as next                       |
| Maintainer creates the proposed branch, then requests implementation | Confirm the actual branch and clean starting tree; implement the agreed issue and checks on that branch                                                                                                    |
| Proposed branch exists only as a suggestion                          | Recommend the name; creating/switching still requires explicit direction                                                                                                                                   |
| Implementation is complete locally                                   | Hand off changes, evidence and limits for local review; the request has not authorized staging or publication                                                                                              |
| Request only a commit message                                        | Return `docs: codify maintainer-led task delivery` as text; Git state stays unchanged                                                                                                                      |
| Several reviewed commits belong to one issue                         | Maintain the same issue branch; each requested commit follows local review; PR assessment covers the whole series                                                                                          |
| Request only PR title/body                                           | Prepare content from the full change and template; return text without push or PR creation                                                                                                                 |
| Explicitly raise a PR with reviewed committed work                   | Discover the default branch, inspect all Git state and existing PRs, push reviewed commits and create/reuse the PR                                                                                         |
| A branch PR already exists                                           | Inspect its base/scope/review, reuse it, and publish requested updates without creating a duplicate                                                                                                        |
| Raise a PR with uncommitted/unreviewed changes                       | Report the files needing review/commit disposition before publication; do not silently stage or omit them                                                                                                  |
| PR feedback requests a correction                                    | Inspect full current scope, implement locally, rerun affected checks and update evidence/content, then use local review and requested commit/publication steps                                             |
| Request or opportunity to self-approve, merge, or enable auto-merge  | Preserve the maintainer-only approval/merge boundary; another task starts when requested after merge                                                                                                       |
| Hypothetical combined #3/#4 delivery                                 | Use a broader branch starting with issue 3; include complete #3 and #4 work with reviewable internal order and separate `Closes #3` and `Closes #4` references; partial #3 work does not make #4 unblocked |
| A blocker has checked boxes or an unmerged PR                        | Keep it undelivered for independent downstream selection; the complete combined-PR exception requires both slices                                                                                          |
| Milestone has no unchecked boxes but lacks integration exit evidence | Report the missing evidence; do not claim completion or close the milestone                                                                                                                                |
| Future milestone is open or a necessary tool is unavailable          | Require deliberate future activation or disclose access/check limits; neither state grants scope or permission                                                                                             |
| Concrete upstream gap or protected filesystem write                  | Use the agreement's specific authorization path; record an actionable handoff when upstream publication is not authorized                                                                                  |

The task-delivery skill routes implementation and commit-message handoff; the
pull-request skill distinguishes content, publication, updates, and feedback;
the experiment skill routes questions/evidence under ADR 0003. Each resolves to
the shared permission owner, preserves issue-comment restrictions, and requires
only available file/Git/GitHub access.

## Experiment-skill exercise: recorded Mermaid evidence

**Question:** What does the existing source-review evidence establish about the
current Mermaid diagrams, and when is a new rendered check required?

**Setup and inputs:** This is a retrospective exercise using the existing
[foundation journal](2026-10-19-foundation-design.md#evidence-limits) and
`docs/architecture/overview.md` at the base revision, not a fresh renderer trial.
The proposed default is to retain accepted diagram source. The alternative is a
new bounded render/reproducer check if current source or a reported failure
requires it. Stop after inspecting the record and current fenced source.

The source portion is reproducible from the repository with the available
Markdown parser:

```sh
git show dbbe2e09a1f8d88dcfe6d42a125bd565688f3ff7:docs/journal/2026-10-19-foundation-design.md
python3 - <<'PY'
from pathlib import Path
from markdown_it import MarkdownIt
tokens = MarkdownIt().parse(Path('docs/architecture/overview.md').read_text())
blocks = [t for t in tokens if t.type == 'fence' and t.info == 'mermaid']
print({'blocks': len(blocks), 'contains_semicolon': [bool(';' in t.content) for t in blocks]})
PY
```

**Observations:** The historical journal records a maintainer-reported rendering
failure involving semicolons in two labels, their replacement, and acceptance of
the corrected documents. It explicitly disclaims an automated rendered-layout
check. Current source inspection finds three Mermaid blocks in the overview,
none containing semicolons; the repository-wide document check finds four
Mermaid blocks in total. These are recorded historical observations and a current
source measurement; no renderer or robot workload was executed.

**Interpretation and decision:** Retain the existing accepted source. The record
supports the source correction and its limited review evidence; it cannot prove
future GitHub rendering or any product behavior. Revisit upon a diagram change
or a reproducible renderer failure, using the then-current renderer/docs and a
minimal failing diagram. The next action is to keep the renderer limitation in
delivery evidence. This exercise adds no product claim or new architecture
decision and needs no infrastructure or upstream publication.

## Initial results and limits

The three skills pass the installed skill-creator metadata validator. Markdown,
relative references, skill/issue-template metadata, requirement/issue coverage,
historical-journal preservation, and diff whitespace checks pass. The document
check covers 30 Markdown files, 514 links (169 local, 327 FleetForge GitHub, and
18 external), seven fenced blocks including four Mermaid blocks, all 114 issue
mappings, 21 milestones, and 30 requirement IDs. External links are parsed, not
exhaustively availability-tested.

Updated #2's 14 supported acceptance checkboxes and replaced its temporary shared
baseline with navigation to the agreement, retaining a default-branch guidance
fallback until merge. Verified the updated body, preserved acceptance/validation
scope, and confirmed that the issue remains open. No issue comment was added.

The three template policy URLs target the agreement's intended default-branch
path; local destinations were verified, and that path becomes available on
GitHub when this delivery merges. Template rendering/discovery in GitHub and
automatic host skill discovery were not exercised. Direct skill file loading
and manual policy walkthroughs do not prove autonomous agent behavior. No sample
PR, push, commit, issue closure, runtime test, or paid/hardware operation was
performed for these walkthroughs. The historical #1 exception is preserved;
the implementation remains available for local maintainer review.

## Contributor review follow-up

The maintainer clarified that public contributors open issues for validation and
submit linked fork PRs into `main`. Exploratory/draft PRs can support issue
validation; maintainers decide the validity of both and approve/merge accepted
changes. Updated CONTRIBUTING.md to own that public process, while the working
agreement owns maintainer-agent local review/publication. GitHub CLI is optional,
installed globally by the contributor, and excluded from repository-managed
dependencies. Documented browser and CLI paths without installing tools.

Read the current MachinePulse
[contribution guide](https://github.com/gleniosp/machinepulse/blob/main/CONTRIBUTING.md)
and [issue forms](https://github.com/gleniosp/machinepulse/tree/main/.github/ISSUE_TEMPLATE)
through authenticated GitHub contents API reads. Compared
[Ruff's bug form](https://github.com/astral-sh/ruff/blob/main/.github/ISSUE_TEMPLATE/1_bug_report.yaml)
and [Rust's bug template](https://github.com/rust-lang/rust/blob/main/.github/ISSUE_TEMPLATE/bug_report.md).
Adapted the common problem/expected-result/reproduction/environment pattern to
FleetForge's present scope. Replaced the initial Markdown issue templates with
three guided YAML forms for bugs, proposals, and delivery tasks, plus chooser
configuration. Internal IDs/priority/milestone/blocker triage belongs to
maintainers. Updated the PR template for linked exploratory and complete work.

Consulted GitHub's [form schema](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema)
and the official [CLI login](https://cli.github.com/manual/gh_auth_login) and
[PR creation](https://cli.github.com/manual/gh_pr_create) references. The temporary
document helper now also rejects duplicate YAML keys, checks form structure,
unique field IDs/required fields and chooser entries, and parses their displayed
Markdown links. This checks the used schema subset; it does not replace GitHub
rendering/submission validation.

The host's subsequent available-skill catalog listed all three repository skills
at their `.agents/skills` paths. That establishes discovery on this host. Removed
the redundant discovery table and manual-loading fallback from root AGENTS.md;
skill descriptions continue to identify when each applies.

Walked through a new bug report with unknown internal metadata, a proposal with
a supporting draft fork PR, an accepted complete fork PR with closure references,
and the web-only and optional-global-CLI contribution paths. The guide/forms
allow each path and keep issue/PR acceptance and merge with maintainers. The
maintainer-agent commit-message request still returns text without changing Git
state. No live report, fork, PR submission, authentication change, or installation
was performed for these scenarios. The revised policy navigation and acceptance
scope are tracked in issue #2; its state remains open.

Follow-up validation passes for 28 Markdown files, four YAML files (three issue
forms with 14 input fields and one chooser), and 530 links including displayed
form/chooser links. All relative destinations, planned default-branch file
destinations, 114 issue mappings, 21 milestones, 30 requirement IDs, historical
journal preservation, and whitespace checks pass. YAML structure validation and
the manual contribution walkthrough do not establish GitHub-rendered appearance
or actual form/PR submission behavior; those remain untested.

## Optional token guidance follow-up

Added optional fine-grained token guidance to CONTRIBUTING.md after checking the
official CLI login/environment, token management, and permission references linked
there. It maps operations to repository permissions, scopes access to the fork or
authorized upstream repository, explains `GH_TOKEN` precedence, and records the
current external-contributor limitations with browser/login alternatives. No
token was created, read, or changed; validation is documentation inspection.
