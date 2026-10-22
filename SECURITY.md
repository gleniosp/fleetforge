# Security policy

## Supported scope

FleetForge is pre-release software. The repository currently contains design
contracts, development tooling, and an agent bootstrap diagnostic; fleet
deployment and its authentication, signature verification, and privilege
boundaries are not implemented. See the [current state](README.md#current-state)
and [threat model](docs/architecture/security.md) before interpreting a design
requirement as a security guarantee.

Maintainers assess reports against current `main`. There are no supported
released versions, maintained release branches, security backport commitments,
or response-time guarantees. Include the source revision in a report. Do not
use this bootstrap as a production robot control or safety system. Development
work belongs in a controlled local environment with trusted participants and
inputs; public-network or untrusted multi-user operation has no verified
security assurance.

## Reporting a suspected vulnerability

Open a **Security concern (initial contact)** issue through the
[issue chooser](https://github.com/gleniosp/fleetforge/issues/new/choose).
Use it to request contact from the repository maintainer,
[gleniosp](https://github.com/gleniosp). Give only a brief description of the
affected area and a source revision if safe to share; a request for contact
alone is sufficient. Do not include exploit instructions, sensitive
reproductions, credentials, private data, or attachments containing them.

A security issue is an ordinary GitHub issue, visible to everyone with
repository access and public when the repository is public. Its title or form
does not make it confidential. Wait for the maintainer to agree a private
follow-up route before providing sensitive details; do not put them in another
issue, PR, or comment. The project currently has no dedicated confidential
contact or verified GitHub private vulnerability reporting service. If a private
route cannot be agreed, this issue process cannot accept sensitive details.

Once a private route has been agreed, provide the affected revision, component,
expected and observed behavior, impact, prerequisites, and a minimal safe
reproduction with sanitized output. Use synthetic data. Exclude live tokens,
passwords, private keys, personal data, and private device, tenant, or network
details. Coordinate any further disclosure with the maintainer.

If you find exposed credentials, revoke or rotate them through the responsible
owner promptly; deleting a post or file does not invalidate a credential or
remove it from clones, caches, or history. Report the location through the
agreed private route without copying the secret. Test only systems and
resources you are authorized to use.

Ordinary defects without sensitive security implications belong in the
[bug report form](https://github.com/gleniosp/fleetforge/issues/new/choose),
following the [contribution guide](CONTRIBUTING.md). Conduct concerns follow the
[code of conduct](CODE_OF_CONDUCT.md).
