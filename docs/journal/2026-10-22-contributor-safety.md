# Licensing, provenance, and contributor safety baseline

- **Date:** 2026-10-22
- **Delivery:** [M0-08, issue #8](https://github.com/gleniosp/fleetforge/issues/8).
- **Source:** Working tree on `docs/8-licensing-provenance-contributor-safety`,
  based on `d8d45730251ed6b403b5c431e1b13d45813af3a4`.
- **Requirement:** [MVP-01](../product/requirements.md#mvp-01--engineering-foundation).

## Delivered scope

Added the approved Apache-2.0 license, a README license statement, inherited
Cargo license metadata, and Pixi workspace license metadata. Downloaded
`LICENSE` unchanged from the [Apache Software Foundation's authoritative
text](https://www.apache.org/licenses/LICENSE-2.0.txt); its SHA-256 is
`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
The upstream appendix remains part of that standard text; the project copyright
statement is in the README. No dependency or lockfile changed.

[Third-party guidance](../../THIRD_PARTY.md) assigns source, version, license,
modification, and notice review to deliveries adding material or distributing
artifacts. It covers dependencies and their transitive contents, code,
documentation, generated images/assets, containers, ROS releases, and cached
package bytes. It distinguishes license permission from digests/signatures and
does not claim a complete distribution audit. No vendored library, new package,
or third-party image was introduced in this delivery.

The contribution guide now links the license and reporting policies, documents
contribution licensing/provenance, and identifies maintainer ownership of project
decisions. The provisional [conduct policy](../../CODE_OF_CONDUCT.md) defines
expectations and moderation, and explicitly identifies missing confidential
conduct contact, independent review, and formal appeal routes.

The maintainer selected GitHub issues for initial security contact. Added a
dedicated form that accepts a contact request alone, with no sensitive
reproduction or exploit details. The [security policy](../../SECURITY.md)
explains that an ordinary issue is visible to repository readers and public if
the repository is public; the maintainer must agree a private follow-up route
before sensitive details are sent. It states the current bootstrap-only support
scope and absence of a dedicated confidential service or response guarantees.
Other issue forms and the PR template point contributors to this policy and ask
them to exclude credentials and private data.

## Sources and compatibility

Consulted the latest official [Cargo license metadata](https://doc.rust-lang.org/cargo/reference/manifest.html#the-license-and-license-file-fields),
[workspace inheritance](https://doc.rust-lang.org/cargo/reference/workspaces.html#the-package-table),
and [Pixi manifest reference](https://pixi.prefix.dev/latest/reference/pixi_manifest/#license-optional)
before changing metadata. Cargo documents workspace inheritance from 1.64;
the installed Cargo is 1.98.1. Verified `license` and `license-file` in the
official [Pixi v0.82.1 schema](https://github.com/prefix-dev/pixi/blob/v0.82.1/schema/schema.json),
matching the installed Pixi 0.82.1 and the project's 0.82.x constraint. Used only
the license fields needed by this task.

Consulted GitHub's [issue-form syntax](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)
and [private vulnerability reporting documentation](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository).
`gh repo view gleniosp/fleetforge --json visibility,url` returned `PRIVATE`.
`gh api repos/gleniosp/fleetforge/private-vulnerability-reporting` returned HTTP
404; this does not establish an available private service. GitHub documents
private vulnerability reporting for public repositories. No repository settings
were changed or private reporting endpoint advertised.

## Validation

Used Linux x86_64, Pixi 0.82.1, Cargo 1.98.1, and prek 0.5.6. Commands and
results:

| Command                                                                       | Result                                                                                      |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `curl -fsSL https://www.apache.org/licenses/LICENSE-2.0.txt \| cmp - LICENSE` | Exact match to Apache's published license text                                              |
| `pixi run --locked cargo metadata --locked --format-version 1 --no-deps`      | Agent resolves `Apache-2.0`, publication remains disabled, zero external Cargo dependencies |
| `pixi run --locked -e dev hooks-check`                                        | Passed repository formatting, Clippy, and hook configuration checks                         |
| `git diff --check`                                                            | Passed                                                                                      |
| `git diff --exit-code -- Cargo.lock pixi.lock`                                | Passed; both lockfiles unchanged                                                            |

An initial hook run was blocked by the sandbox's access to prek's log cache; the
same repository command passed after access was granted. Manually reviewed the
changed documents, form structure and required fields, and local link targets.
The forms have not been rendered by GitHub.

Manually reviewed the changed policies and examples for credential/private-data
content and unsupported security claims. Reviewed the security-report flow: an
ordinary bug retains reproduction fields; a sensitive finding uses the
initial-contact form without posting its details; further sensitive evidence
waits for an agreed private route. Reviewed that provenance obligations retain
upstream licenses and notices rather than claiming that Apache-2.0 covers
dependencies. The conduct text is original project policy rather than an
attributed external conduct template.

## Limits and handoff

GitHub has not rendered or accepted these new forms from a published default
branch. YAML/source review does not establish hosted form behavior. No private
report, moderation action, or private follow-up service was exercised. A
confidential follow-up route must be arranged for an actual sensitive report;
the initial issue does not provide confidentiality. Independent conduct review
and formal appeals remain explicit policy decisions.

Runtime code did not change, so application unit tests were not repeated for
this documentation/metadata delivery. A future artifact distributor must perform
the concrete upstream license/notice audit for the shipped contents. Changes
are available for local maintainer review; no staging, commits, or publication
were performed.
