# Third-party provenance and distribution

FleetForge's [Apache-2.0 license](LICENSE) covers original project material.
Dependencies, copied or adapted source, documentation excerpts, images, and
release inputs retain their own licenses. A lockfile or content digest records
identity or integrity; it does not establish permission to use or redistribute
the material.

## Contributions

For each added or updated third-party item, give reviewers its upstream source,
version or commit, license and license-text location, required notices, and any
local modifications. Keep this information beside vendored material or in the
owning delivery's documentation. Preserve copyright, license, and attribution
notices; identify modified files as required by the upstream terms. Do not copy
material with unknown or incompatible permissions into the repository.

For generated or externally supplied assets, including AI-assisted assets,
record their origin, relevant tool/source and usage terms, and any supplied
references. Review rights to those references and to the resulting asset before
inclusion. Avoid personal data, secrets, or unsupported ownership claims.

## Dependencies and tools

When a dependency changes, inspect its license and those of the resolved
transitive dependencies for the intended use and distribution. Record the
review and any notice/source obligations in the delivery evidence. Distinguish
development tools from code and libraries shipped in an executable or runtime;
packaging an environment can also redistribute its tools. Package metadata
helps locate upstream terms but does not replace reviewing them.

The current Rust diagnostic uses the standard library and has no external Cargo
dependencies. Pixi provisions development/build tools and their transitive
packages. Their presence in an installed environment does not relicense them
under Apache-2.0 or constitute a completed redistribution audit. The current
dependency identities are in `Cargo.lock` and `pixi.lock`.

The [unsigned ROS workload fixtures](examples/ros-workloads/README.md) have
independent runtime locks record the resolved package identities and declared
licenses. Their
[delivery review](docs/journal/2026-10-26-ros-workloads.md#dependency-provenance-review)
records direct/transitive provenance findings and the limits of this source-only
delivery.

## Images and release artifacts

Before distributing a container image, executable, archive, ROS workload,
release descriptor, or cached package collection, the delivery owner must:

- Inventory the included base image, packages, libraries, application files,
  and other assets, including transitive contents; retain source URLs and exact
  versions or digests so the shipped bytes can be traced.
- Review each item's redistribution terms and satisfy applicable license,
  attribution, modification, source-offer/source-availability, and notice
  requirements. Include the applicable license texts and notices in the
  distribution, accessible to its recipients.
- Retain upstream `NOTICE` material when required, and add a distribution notice
  inventory when there are actual notices to carry. Do not invent attributions
  or imply that FleetForge's license replaces upstream terms.
- Check for credentials, private data, and unintended files in build contexts,
  image layers, logs, and archives. Record review results and unresolved items
  before publication under the [working agreement](docs/working-agreement.md).

These responsibilities apply to pre-provisioned package bytes as well as
installed environments. Runtime release signatures and digests establish the
[planned trust boundary](docs/architecture/security.md); they do not certify
license compliance. This bootstrap policy does not claim a completed audit of
future containers, ROS releases, or package-cache distributions. Each delivery
that introduces or publishes those artifacts owns its concrete inventory and
evidence.
