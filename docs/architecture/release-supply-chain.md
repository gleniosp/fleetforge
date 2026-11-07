# Release, package and artifact lifecycle

**Status:** MVP signed release and local provisioning contracts are accepted in
the [release specification](../specs/releases.md) and
[release provisioning guide](../guides/release-provisioning.md). The wider
pipeline below is deferred; it does not claim current CI or hosted services.

Developer → source review → build/test → provenance/SBOM → publisher signature
→ package publication → release registration → separate approval/promotion →
authorized deployment intent → byte delivery → device verification → activation
and health → observation/recovery.

The package provider stores Conda package bytes and an index. A FleetForge
release registry would bind immutable release identity, descriptor digest,
compatibility, provenance and promotion status. An artifact delivery provider
transfers authorized bytes or fills a cache. The deployment authority alone
selects desired software for an assignment. Publishing, downloading or training
an artifact does not grant deployment authority. The device verifies publisher
trust, exact bytes and compatibility before preparation, including when offline.

| Candidate                                         | Benefit to evaluate                                                                         | Cost or risk to test                                                                                   |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Prefix.dev public/private Conda channels          | Existing channel hosting and Pixi client workflow can simplify initial package distribution | External service, access/availability and channel-policy dependence; a channel is not release approval |
| Other hosted Conda channel                        | Provider diversity                                                                          | Authentication, indexing, retention and export semantics differ                                        |
| Self-hosted/object-backed channel or local mirror | Local control and offline provisioning                                                      | Index maintenance, authorization and operational burden                                                |

[Prefix.dev's current channel documentation](https://prefix.dev/docs/prefix/channels)
describes package hosting, and its [publishing guide](https://prefix.dev/docs/prefix/channels/publish-packages)
states that upload stores an artifact without proving its suitability. This is
a provider candidate, not a FleetForge registry or a selected production
dependency. [#169](https://github.com/gleniosp/fleetforge/issues/169) records
the comparison; a later activated delivery must verify the chosen provider with
the project's Pixi version, locks, fresh offline install and credential policy.

The local catalog remains the MVP registry boundary. Future
[#51](https://github.com/gleniosp/fleetforge/issues/51) specifies protected
catalog updates, [#64](https://github.com/gleniosp/fleetforge/issues/64) real
authorized transfers, [#96](https://github.com/gleniosp/fleetforge/issues/96)
resume/corruption behavior and [#100](https://github.com/gleniosp/fleetforge/issues/100)
production signing metadata. [#158](https://github.com/gleniosp/fleetforge/issues/158)
attaches provenance/SBOM to immutable subjects. A channel named stable, beta or
canary would be a promotion policy in FleetForge, never an inference from a
package URL. Keep known-good inputs through failed promotion, download,
activation and recovery.
