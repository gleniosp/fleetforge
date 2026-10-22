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

Use **Security → Report a vulnerability** in this repository to submit a
confidential report through
[GitHub Private Vulnerability Reporting](https://github.com/gleniosp/fleetforge/security/advisories/new).
Do not report vulnerabilities through public GitHub issues, pull requests, or
comments.

Reports reach maintainers privately through GitHub Security Advisories.
Maintainers receive notifications, including email, and will reply in the
private report. Coordinate any further disclosure with the maintainer.

Provide the affected revision, component, expected and observed behavior,
impact, prerequisites, and a minimal safe
reproduction with sanitized output. Use synthetic data. Exclude live tokens,
passwords, private keys, personal data, and private device, tenant, or network
details.

If you find exposed credentials, revoke or rotate them through the responsible
owner promptly; deleting a post or file does not invalidate a credential or
remove it from clones, caches, or history. Report the location in the private
report without copying the secret. Test only systems and resources you are
authorized to use.

Ordinary defects without sensitive security implications belong in the
[bug report form](https://github.com/gleniosp/fleetforge/issues/new/choose),
following the [contribution guide](CONTRIBUTING.md). Conduct concerns follow the
[code of conduct](CODE_OF_CONDUCT.md).
