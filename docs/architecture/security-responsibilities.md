# Future security responsibilities

**Status:** Planning boundary, not production assurance. The
[MVP threat model](security.md) owns current required controls. Production
release trust, enrollment and independent audit belong to
[FUT-06](future.md#fut-06--production-security); device lifecycle and
tenant isolation have separate [FUT-14](future.md) and
[FUT-09](future.md#fut-09--tenancy) owners.

| Role                          | May authorize                                            | Must not implicitly authorize                                                    |
| ----------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Publisher                     | Immutable signed release subject                         | Deployment to a device or tenant                                                 |
| Release approver              | Promotion of a trusted subject under policy              | Generation allocation or publisher key use                                       |
| Deployment operator/authority | Scoped desired state after authentication and policy     | Signing arbitrary publisher content or changing device-local execution truth     |
| Robot agent                   | Locally verify/execute accepted intent and recover       | Accepting peers, artifacts or model candidates merely because they are reachable |
| Cloud administrator           | Infrastructure and service operation                     | Tenant deployment, publisher approval or reading protected datasets by default   |
| Data collector                | Scoped capture/upload under consent and retention policy | Training use or deployment approval                                              |
| Training/evaluation service   | Produce candidate and measured evidence                  | Publisher trust, release approval or deployment intent                           |
| Commercial service            | Usage/entitlement records from authorized observations   | Robot safety control or direct command execution                                 |

Device identity needs protected credentials, enrollment/claim, rotation,
revocation, quarantine, retirement and lost-state recovery. Hardware roots and
verified boot are target-specific evaluations, not prerequisites for the MVP.
Release and model supply chains need immutable digests, signer custody,
provenance, SBOM, compatibility and compromise response. Host and workload OS
permissions remain separate. Cloud API, jobs, queues, object storage and
database roles must enforce tenant boundaries independently; an authenticated
gateway cannot substitute for backend authorization. Browser sessions require
CSRF/XSS protections; data capture needs consent, minimization and retention.

Threat modeling and negative tests must cover forged producer/publisher,
cross-tenant reads/uploads, stale authority, replay, malicious artifact paths,
compromised credentials, offline revocation delay, exporter backpressure,
unavailable queues and restore from stale backups. Security records need actor,
scope, decision, source time and bounded retention without secret content.
[#62](https://github.com/gleniosp/fleetforge/issues/62) owns independent
production review and incident recovery. New optional data and commercial
issues must specify their own negative tests rather than treating #62 as a
catch-all implementation issue.
