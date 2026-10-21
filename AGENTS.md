# FleetForge agent guidance

FleetForge is a local-first, Pixi-native robot software lifecycle project.
Read [README.md](README.md) for the current implementation state and the
[documentation map](docs/README.md) for the owner of each contract.

The [working agreement](docs/working-agreement.md) owns task selection,
authorization, validation, local review, commits, and publication. Read its
applicable sections before acting. Repository instructions and skills route to
that policy; they do not grant additional permissions. Scoped `AGENTS.md` files
add guidance for their directories; [docs/AGENTS.md](docs/AGENTS.md) applies to
documentation changes.

Introduce executable setup and checks with the delivery that owns them; current
toolchain availability is described in [CONTRIBUTING.md](CONTRIBUTING.md).
Keep essential implementation, validation, configuration, documentation, and
decision/evidence changes together under the working agreement's
[readiness rules](docs/working-agreement.md#implementation-and-readiness).

- Before changing or explaining package-management configuration or behavior,
  consult the package manager's latest official documentation and check
  compatibility with the version used by the project.
- Start with the documented minimal configuration. Check transitive dependencies
  and host prerequisites before adding packages; justify each direct dependency
  by a present need and its development, build or runtime role. Follow
  [ADR 0003](docs/adr/0003-bounded-decisions-and-evidence.md) for proportionate
  validation and experiments; distinguish documented behavior from assumptions.
