# Check release files and prepare a local catalog

Imagine you have application versions **A** and **B**. Before a robot can run
either one, its release files must be available locally and match their recorded
contents. This guide explains the tools that check and copy those files today.

Start with [From approved software to a running robot](releases-explained.md) for
the full deployment story. Here we will use the same ideas for a smaller,
executable example: prepare separate local folders representing the inputs an
authority and a robot would receive.

The current tools check **integrity**: whether the files match the release's
recorded definition. They do not yet check the publisher's signature or run a
deployment. Their output includes `integrity_only: true` to make that boundary
visible. Signature verification belongs to
[#86](https://github.com/gleniosp/fleetforge/issues/86).

## Who does what?

Several roles can exist on the same computer during development. Their
responsibilities still differ:

| Part             | Responsibility                                                                                     | Role in this example                                                                     |
| ---------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Contributor host | Runs the FleetForge repository's development tools                                                 | Runs both commands from the root `host` Pixi environment                                 |
| Publisher        | Approves a release by signing its descriptor                                                       | Signature creation and verification are subsequent work; A/B are unsigned fixtures       |
| Provisioner      | Places release inputs and a catalog on each machine that needs them                                | The contributor runs `release-provision` to prepare local fixture folders                |
| Authority        | Records and sends the desired release for a device                                                 | Its fixture folder receives a copy of the release inputs; no authority service runs here |
| Device agent     | Accepts authorized intent, prepares the application's environment, supervises it and checks health | Its device fixture folder receives another copy; no agent deployment runs here           |
| Application      | Performs the robot's actual work inside its own environment                                        | A and B contain real ROS application code, but these commands do not start it            |
| Pixi             | Manages dependencies, lockfiles and installed environments                                         | Checks manifest/lock consistency; installation is a later step                           |

In the planned deployment flow, these responsibilities connect like this:

```text
Publisher approves a release
          |
          v
Trusted local setup (the provisioner)
          |
          +--> Authority: release inputs and catalog
          |       |
          |       +-- desired release instruction --> Device agent
          |
          +--> Device: release inputs and catalog ------^
                                                        |
                                              agent asks Pixi to prepare
                                                        |
                                                        v
                                              Application environment
                                                        |
                                              agent starts/checks app
```

This diagram shows the accepted design. The authority's instruction identifies
which release to run; it does not supply the release files. The MVP expects
trusted setup to put those files on each machine first. Publisher approval and
authority deployment instructions are also separate: approving B as valid
software does not by itself request that a particular robot switch to B.

## Keep the three software resources separate

A release folder is a fixed definition of the application and its runtime inputs.
It contains application code, a descriptor (`release.json`), a manifest
(`pixi.toml`) and a lockfile (`pixi.lock`). The descriptor lists the expected
files, their sizes and their fingerprints, plus starting and health instructions.

Two more resources are needed when installing and running the application:

```text
Release inputs                 Cached dependency packages
--------------------------     --------------------------
App code and instructions      Actual downloadable package bytes
Manifest and lockfile           Needed locally for a fresh offline install
          |                                |
          +---------------+----------------+
                          |
                      Pixi installs
                          |
                          v
                 Installed environment
                 ---------------------
                 Python, ROS and other dependencies
                 Used to run this release's application
```

`release-provision` copies only **release inputs** and creates their catalog.
It does not copy package caches or installed `.pixi` environments. A lockfile
records which packages are needed; it does not contain those packages. Proving
a fresh installation from cached packages is owned by #14.

The root repository's `host` environment contains contributor tools, including
this checker. A and B each have their own manifest and lockfile for their own
application environment. Running a root `host` task does not install Python or
ROS for either application.

## What is a catalog?

A **catalog** is a local index. For each release it records a stable release ID,
the fingerprint of its descriptor, and the directory containing its files.
**Digest** is another word for that fingerprint.

For example, a catalog entry means: “`ros-counter-a-v1` has this exact descriptor
fingerprint, and its files are in the `ros-counter-a-v1` directory beneath this
release root.” Directory names alone do not establish release identity.

```text
Provisioned release root
├── catalog.json                  Index of available releases
├── ros-counter-a-v1/
│   ├── release.json              A's definition and file fingerprints
│   ├── pixi.toml                 A's dependency declarations
│   ├── pixi.lock                 A's resolved dependencies
│   └── app/                      A's application code
└── ros-counter-b-v1/
    └── ...                       B's independent inputs
```

The catalog is an index, not proof of publisher approval. A changed file should
fail its fingerprint check. A changed descriptor should fail the catalog's
fingerprint check. Authenticating the publisher will add another check in #86.

## Prepare authority and device fixture folders

Run these commands from the repository using host-installed Pixi. Choose an
existing parent directory that you control, with no symlinks in its path. On
Linux, this disposable example uses `/tmp`:

```sh
mkdir -p /tmp/fleetforge-fixtures
pixi run --locked -e host release-provision /tmp/fleetforge-fixtures/authority
pixi run --locked -e host release-provision /tmp/fleetforge-fixtures/device-1
```

These commands run on the **contributor host**. The folder names describe their
intended fixture roles; they do not start services, create a robot or connect to
another machine. Both receive independent copies of A and B:

```text
Repository releases/                   Contributor host
       |                                      |
       +-- release-provision -----------------+
                                              |
                      +-----------------------+-------------------+
                      v                                           v
          authority fixture folder                   device-1 fixture folder
          catalog + A/B inputs                       catalog + A/B inputs
```

The tool checks a temporary staging copy before publishing the complete folder.
If the destination already exists, it must validate and match the new catalog
exactly. Repeating the same operation succeeds without changing the destination;
conflicting contents are rejected. A release ID cannot silently acquire a new
descriptor fingerprint.

By default, the source is the repository's `releases/` directory. Use
`--source PATH` to select a different trusted source containing the A/B folders.
This command is a fixture provisioner for these two releases, rather than a
general release publishing or remote file transfer service.

## Check the prepared files

Check every catalog entry, or select one release:

```sh
pixi run --locked -e host release-check /tmp/fleetforge-fixtures/device-1
pixi run --locked -e host release-check /tmp/fleetforge-fixtures/device-1 \
  --release-id ros-counter-a-v1
```

Add `--digest sha256:...` with `--release-id` when you want to check a specific
requested descriptor fingerprint too. Catalog directories always resolve beneath
the supplied release root. An unknown ID fails; the checker does not search for
or download missing releases.

The checker answers these questions:

1. Does the catalog have the expected structure, unique IDs and safe paths?
2. Does each descriptor have the expected structure and exact canonical encoding?
   Canonical encoding gives a descriptor one precise byte representation for hashing.
3. Does its identity match the catalog and any requested fingerprint?
4. Are all expected files present, with the recorded sizes and fingerprints,
   and no unexpected files? Are working directories and health timings valid?
5. Do the manifest and lockfile agree according to Pixi?

A **schema** describes the allowed fields and values of a JSON document. Checking
a schema catches mistakes such as a missing release ID or an unknown field.
Fingerprint and filesystem checks answer additional questions a schema cannot,
such as whether `app/main.py` actually contains the expected bytes.

For example, if someone edits A's `app/main.py` after provisioning, A's recorded
fingerprint no longer matches. `release-check` fails instead of treating that
folder as an intact copy of A. The tool checks temporary copies and leaves the
source release files and locks untouched. Passing means the integrity checks
succeeded; publisher authenticity and application health still require their
own checks.

## Implementation boundaries and failure handling

The implementation in [catalog.py](../../tools/releases/catalog.py) bounds input
sizes and JSON nesting, rejects duplicate JSON members and unsafe paths, and
rejects symlinks, hard-linked payloads and special files such as FIFOs. It traverses
source directories using pinned handles rather than relying on a path string
check. The [release contract](../specs/releases.md) owns exact limits, canonical
encoding rules and error names.

The current adapter accepts the fixtures' binary Conda manifests: `workspace`
and string-valued `dependencies`, targeting only `linux-64`. Other manifest forms
reject before invoking Pixi. Host-installed Pixi 0.83.0 checks a disposable copy
using `lock --check --offline --no-config`, with a 60-second deadline. The
[official command reference](https://pixi.prefix.dev/latest/reference/cli/pixi/lock/)
and installed 0.83.0 help describe `--check` as implying `--dry-run`. This check
can fail because inputs disagree or offline solver metadata is unavailable;
it does not prove that cached packages are sufficient for an offline installation.

Optional signature envelopes are copied with a 4 KiB limit but are not verified
yet. #86 must add publisher verification before payload/Pixi validation and
before any trusted execution path uses these inputs. The existing ROS
demonstrations remain developer-owned unsigned experiments.

Keep destination parents and release inputs protected from application writes.
Run one provisioner at a time for a destination; concurrent writers and durable
runtime database bindings belong to later deliveries. Allow disk space for
staging copies as well as the destination. Input size limits do not reserve space.

## Supporting tools and checks

The shared schemas live in [`schemas/releases/v1/`](../../schemas/releases/v1/).
The written [release specification](../specs/releases.md) explains their rules.
The current checker reads schemas from this checkout; future application builds
will package or embed them from that same source. This keeps publisher and agent
contracts aligned without making installed applications depend on the docs tree.

Two host dependencies help the checker use these schemas:

- `jsonschema` validates JSON against the repository's Draft 2020-12 schemas.
- `referencing` supplies their local schema registry, so schema links resolve
  from repository files without fetching schemas from the network.

They support contributor-side validation; they add no managed-device runtime
requirement. The mypy exception for `jsonschema` tolerates that library's missing
type information while keeping our own Python code in the normal type checks.

Run `pixi run --locked -e host python-test` for the portable integrity and workload
helper regressions. Host Python checks include the checker, provisioner and tests.
The [delivery journal](../journal/2026-10-30-release-integrity.md) records checks
actually performed and their limits.
