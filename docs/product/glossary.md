# Glossary

Shared definitions of FleetForge concepts and supporting technical terms.
Use this page to look up a term; the
[release walkthrough](../guides/releases-explained.md) introduces concepts through
one connected example. [Requirements](requirements.md) specify required behavior;
architecture and specifications own the detailed rules linked from each entry.

## Acceptance

The agent has validated and durably committed an instruction. Execution may
still be pending: receiving or accepting the instruction does not establish
that the requested software is running. See
[durable acceptance](../architecture/coordination.md#durable-authority-and-acceptance).

## Active release

The software associated with the actual managed workload. Its absence or an
unknown state must be represented explicitly. See
[deployment and recovery](../architecture/overview.md#deployment-and-recovery).

## Agent

The service on a managed device that owns local execution, health and recovery.
An agent process is distinct from the device's persistent identity. See
[the deployment roles](../guides/releases-explained.md#publisher-authority-and-device-have-separate-powers).

## Asset

The maintainable robot, identified by `asset_id`. It can keep its identity when
an attached computer is replaced. See the
[identity model](../architecture/identity.md#identity-model).

## Assignment

The binding of an asset, device, owning tenant and logical deployment authority,
identified by `assignment_id`. See
[assignment and history](../architecture/identity.md#assignment-and-history).

## Authority

The single logical deployment writer for an assignment, identified by
`authority_id`. It records which software devices should run; its identity is
separate from its host or process. See
[authority and acceptance](../architecture/coordination.md#durable-authority-and-acceptance).

## Automatic recovery

Restoring and verifying known-good software after a failed deployment. See
[failure and recovery](../guides/releases-explained.md#what-can-fail-and-what-stays-running).

## Canonical encoding

One prescribed way to write a document's bytes, including property order and
spacing. It lets tools calculate matching hashes and signatures. See
[canonical JSON](../guides/releases-explained.md#a-few-details-the-tooling-handles).

## Dependency, direct and transitive

A **dependency** is software another program needs. A **direct dependency** is
declared by the project itself. A **transitive dependency** is brought in because
another dependency needs it. Both become part of the resolved environment; see
the [workload dependency example](../../examples/ros-workloads/README.md#runtime-dependencies-and-upgrades).

## Deployment attempt

A correlated effort to satisfy an accepted generation, covering the work and
its outcome. See [deployment and recovery](../architecture/overview.md#deployment-and-recovery).

## Descriptor

A release's `release.json`: its contents list and instructions for starting and
checking the application. See [release descriptors](../guides/releases-explained.md#add-a-contents-list-and-instructions-the-descriptor).

## Desired state

The authorized target release and descriptor digest for an assignment/device
at a particular generation. See
[desired state and reconciliation](../architecture/overview.md#desired-state-and-reconciliation).

## Device

The managed computer or endpoint, identified by `device_id`. It is distinct
from the robot asset and from the agent process running on it. See the
[identity model](../architecture/identity.md#identity-model).

## Digest and hash

A **hash** or **digest** is a fingerprint calculated from exact bytes. It helps
detect changed files but does not identify who approved them. See
[fingerprints and hashing](../guides/releases-explained.md#check-whether-files-changed-fingerprints-and-hashing).

## Durable event

A persisted record in bounded operational history. These events are separate
from process output and security decision records. See
[observability and freshness](../architecture/overview.md#observability-and-freshness).

## Entrypoint

The command used to start an application, together with its working directory.
See the [descriptor example](../guides/releases-explained.md#add-a-contents-list-and-instructions-the-descriptor).

## Environment and activation

An **environment** is an installed set of software packages used to run a
program. **Environment activation** sets variables so the program can find those
packages. This differs from **deployment activation**, when FleetForge switches
the running workload. See [the release journey](../guides/releases-explained.md#the-complete-journey-to-the-robot).

## Fixture

A deliberately prepared example used for a repeatable check. It can be data,
files or a runnable setup. FleetForge has both
[document review fixtures](../specs/fixtures/releases/README.md) and
[runnable ROS examples](../../examples/ros-workloads/README.md).

## Fleet

A configured selection of assets/devices, independent of their network
addresses. See the [MVP boundary](requirements.md#fixed-mvp-boundary).

## Generation

A durable, increasing counter scoped to one authority/assignment/device.
It orders desired-state instructions. See
[coordination rules](../architecture/coordination.md#durable-authority-and-acceptance).

## Health probe

A small program that checks whether the workload actually behaves as expected.
A running process alone is not enough. See
[how health is checked](../guides/releases-explained.md#why-health-includes-process-identity-and-a-fresh-challenge).

## Immutable

Fixed once published. Changing a release's inputs requires a new release ID,
so a later retry cannot silently run different software under the same name.
See [collecting a software version](../guides/releases-explained.md#first-collect-one-software-version-into-a-release).

## Known-good release

Software that previously passed workload health verification. See
[deployment and recovery](../architecture/overview.md#deployment-and-recovery).

## Manifest and lockfile

A **manifest** declares the software packages a project needs. A **lockfile**
records the resolved package versions and identities. Neither contains the
dependency package bytes themselves. See
[release inputs and environments](../guides/releases-explained.md#first-collect-one-software-version-into-a-release).

## Nonce

A fresh, unpredictable challenge value used for one health check. The workload
must return it through ROS, helping distinguish a current reply from an old
one. See [fresh health challenges](../guides/releases-explained.md#why-health-includes-process-identity-and-a-fresh-challenge).

## Observation

The last received source snapshot, carrying identity, sequence, source time
and freshness information. It describes what was observed; it may be stale.
See [bounded synchronization and freshness](../architecture/coordination.md#bounded-synchronization-and-freshness).

## Operator

The person requesting changes through the console. Architecture descriptions
also use **operator** for the authority's local service/UI role. The
[deployment walkthrough](../guides/releases-explained.md#publisher-authority-and-device-have-separate-powers)
distinguishes the person's request from the authority service's responsibilities.

## Process-instance ID

A fresh identifier for one running attempt of the application. Restarting the
same release creates a new instance. See
[health and process identity](../guides/releases-explained.md#why-health-includes-process-identity-and-a-fresh-challenge).

## Provenance

Where software came from: its upstream project, version and package source.
FleetForge also records license information for dependency review. See the
[workload dependency review](../../examples/ros-workloads/README.md#dependency-review).
Provenance records do not replace publisher signature verification.

## Release

A fixed definition of one application version: an immutable publisher-signed
descriptor together with its application, Pixi manifest and lockfile inputs.
The unsigned examples demonstrate runtime behavior before publisher approval
is established. See the [release walkthrough](../guides/releases-explained.md#first-collect-one-software-version-into-a-release)
and [exact release contract](../specs/releases.md#documents-and-identity).

## Release catalog

A local index mapping supported release IDs to immutable descriptors/digests
and the directories containing their files. See
[finding a release on disk](../guides/releases-explained.md#find-b-on-disk-the-catalog).

## Request ID

An identifier used to recognize retries. API submission and instruction
delivery have separate request identities. See
[coordination rules](../architecture/coordination.md#durable-authority-and-acceptance).

## Requested rollback

An explicit request for a new generation targeting a retained previous release.
See [rollback and recovery](../guides/releases-explained.md#what-can-fail-and-what-stays-running).

## ROS 2, Jazzy and RoboStack

**ROS 2** supplies libraries and tools for robot programs to communicate.
**Jazzy** is the ROS 2 distribution used by these workloads. **RoboStack** packages
ROS software for installation into environments such as those managed by Pixi.
See the [tested workload runtime](../experiments/0002-ros-workload-runtime.md).

## ROS domain, topic and lifecycle

A **domain** separates ROS discovery and communication groups. A **topic** is a
named message channel. A managed node's **lifecycle** includes states such as
inactive and active. These examples use all three to check the intended
application; see the [workload interface](../../examples/ros-workloads/README.md#workload-and-probe-interface).

## Runtime and workload

The **workload** is the application FleetForge manages. Its **runtime** is the
software environment needed to execute it, separate from contributor build and
checking tools. See [independent release environments](../guides/releases-explained.md#first-collect-one-software-version-into-a-release).

## Tenant

The owning organization or context, identified separately by `tenant_id`.
See [assignment and history](../architecture/identity.md#assignment-and-history).
