# Release descriptor and catalog design review — 2026-10-24

## Scope and repository input

[M1-01 (#10)](https://github.com/gleniosp/fleetforge/issues/10) specifies the
[version 1 release contract](../specs/releases.md), machine-readable schemas,
illustrative A/B byte vectors and rejection expectations. The working tree is
based on `b81ffe381ed9eb072f052e1dc850de369d17af81` on
`docs/10-release-descriptor-catalog`. Its prerequisite #9 was delivered by
[merged PR #123](https://github.com/gleniosp/fleetforge/pull/123), merge commit
`9b80b4a146a198808d8c47c46ed420863d3e14d6`. No runtime trust/release capability
is claimed by this design delivery.

## Sources and compatibility

Reviewed on 2026-10-24: [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785),
[RFC 8032](https://www.rfc-editor.org/rfc/rfc8032), [JSON Schema Draft
2020-12](https://json-schema.org/draft/2020-12/json-schema-core), and the
[latest official Pixi install reference](https://pixi.prefix.dev/latest/reference/cli/pixi/install/).
Local `pixi --version` reported 0.83.0, matching the repository minimum.
`pixi install --help` confirmed locked freshness checks and offline missing-cache
failure semantics. These observations support the contract's flag compatibility;
no Pixi/ROS install or offline-cache experiment ran for this issue.

## Reproducible schema and byte-vector review

Run from the repository root. The review environment already supplied Python
3.14.4 and jsonschema 4.19.2; they were used as diagnostic tools without adding
project dependencies or changing locks. A reviewer needs those tools available
to repeat this optional schema review; this is not a new canonical project task.

```sh
python3 - <<'PY'
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

root = Path('docs/specs').resolve()
fixture = root / 'fixtures/releases'
schemas = {p: json.loads(p.read_text()) for p in (root / 'schemas').glob('*.json')}
registry = Registry().with_resources(
    (p.as_uri(), Resource.from_contents(s)) for p, s in schemas.items()
)
for value in schemas.values():
    Draft202012Validator.check_schema(value)
def validator(name):
    return Draft202012Validator(
        {'$ref': (root / 'schemas' / name).as_uri()}, registry=registry
    )
def load(name):
    return json.loads((fixture / name).read_text())
payloads, vectors = load('payloads.json'), load('vectors.json')
release = validator('release.schema.json')
for label in ('a', 'b'):
    descriptor = load(f'release-{label}.json')
    release.validate(descriptor)
    # This shortcut is valid for these ASCII/integer-only objects, not all JCS.
    raw = json.dumps(descriptor, sort_keys=True, separators=(',', ':')).encode()
    vector = vectors[label]
    assert raw == bytes.fromhex(vector['canonical_utf8_hex'])
    assert vector['descriptor_digest'] == 'sha256:' + hashlib.sha256(raw).hexdigest()
    assert bytes.fromhex(vector['signature_message_hex']) == b'FleetForge.release.v1\0' + raw
    paths = [entry['path'] for entry in descriptor['files']]
    assert paths == sorted(set(paths)) == sorted(payloads[label])
    for entry in descriptor['files']:
        content = payloads[label][entry['path']].encode()
        assert entry['size'] == len(content)
        assert entry['sha256'] == hashlib.sha256(content).hexdigest()
    for path in ('../escape', '/tmp/x', 'app//x', 'app/./x', 'app/../x',
                 'C:\\x', 'app\\x', '%2e%2e/x', 'app/x\n'):
        bad = copy.deepcopy(descriptor)
        bad['files'][0]['path'] = path
        assert not release.is_valid(bad), path
    for key, value in [('schema_version', 2), ('platform', 'linux-aarch64'),
                       ('unknown_field', True)]:
        bad = copy.deepcopy(descriptor)
        bad[key] = value
        assert not release.is_valid(bad), key
for name, schema in [('catalog.json', 'catalog.schema.json'),
                     ('keyring.json', 'keyring.schema.json'),
                     ('signature-shape.json', 'signature.schema.json')]:
    validator(schema).validate(load(name))
catalog = load('catalog.json')['releases']
assert len({e['release_id'] for e in catalog}) == len(catalog) == 2
assert len({e['directory'] for e in catalog}) == 2
for entry, label in zip(catalog, ('a', 'b')):
    assert entry['release_id'] == load(f'release-{label}.json')['release_id']
    assert entry['descriptor_digest'] == vectors[label]['descriptor_digest']
assert vectors['a']['descriptor_digest'] != vectors['b']['descriptor_digest']
print('5 schemas, 5 fixture documents, A/B vectors and 24 schema mutations: passed')
PY
```

Result: passed. Each descriptor had four payload entries with matching exact-byte
sizes and SHA-256 hashes. The canonical and domain-separated message vectors
matched recomputation. Catalog IDs/digests matched both descriptors. The envelope
passed shape validation only; its all-zero signature is deliberately invalid.

## Repository checks

Configured repository hooks were run with explicit changed and untracked paths
so new schemas/fixtures were included without staging. Reproduce with:

```sh
python3 - <<'PY'
import subprocess
changed = subprocess.check_output(['git', 'diff', '--name-only'], text=True).splitlines()
new = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], text=True).splitlines()
subprocess.run(['pixi', 'run', '--locked', '-e', 'host', 'prek', 'run',
                '--stage', 'pre-commit', '--files', *changed, *new], check=True)
PY
git diff --check
```

Result: all applicable hooks passed (case/merge conflicts, file size, JSON,
final newlines, whitespace and hook configuration); TOML/YAML checks skipped
because no corresponding files changed. The first attempt could not open
Prek's cache log under the filesystem sandbox; the authorized retry with cache
access passed. `git diff --check` passed. Lockfiles and executable setup were
unchanged.

Relative documentation links/fragments, fenced blocks and final newlines were
also checked across changed/new Markdown using:

```sh
python3 - <<'PY'
from pathlib import Path
import re
import subprocess
files = subprocess.check_output(['git', 'diff', '--name-only'], text=True).splitlines()
files += subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], text=True).splitlines()
count = 0
for name in files:
    path = Path(name)
    if path.suffix != '.md':
        continue
    text = path.read_text()
    assert text.endswith('\n') and len(re.findall(r'^```', text, re.M)) % 2 == 0
    for link in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', text):
        if '://' in link or link.startswith('mailto:'):
            continue
        target, _, fragment = link.partition('#')
        dest = path.parent / target if target else path
        assert dest.exists(), (name, link)
        if fragment and dest.suffix == '.md':
            headings = re.findall(r'^#+\s+(.*)$', dest.read_text(), re.M)
            slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings]
            assert fragment in slugs, (name, link)
        count += 1
print(f'Checked {count} relative links/fragments, fences and final newlines')
PY
```

Result: 138 relative links/fragments passed. This is a source-level check of
the current headings, not a rendered Markdown or external-URL availability test.
No Mermaid source changed. Manual full-diff/schema/fixture review found no
unrelated changes or claims of executable runtime enforcement.

## Manual contract review and limits

Manually reviewed every row in the [fixture matrix](../specs/fixtures/releases/README.md#review-matrix)
against schemas and validation order: altered descriptor/payload bytes, missing
signature or key, key/signature substitution, ID collisions, malformed paths,
unsupported targets, limits and stale ROS identity/challenge. Unsupported version
and algorithm dispatch and a missing-signature exception have explicit error
precedence. Schemas deliberately leave cross-file relationships, aggregate limits,
path ownership, cryptographic validity and process observations to their semantic
owners. A shape pass cannot authorize installation or health execution.

The examples contain placeholder manifest/lock/application text. No fixture
signature was generated/verified; no general JCS implementation was tested.
No real symlink attack, install/process side effect, ROS health behavior, package
compatibility, key replacement or cache-isolation scenario was executed. Those
require the actual implementations in #11, #13, #14, #20 and #86; the contract
and matrix define their required behavior. Existing runtime tests were not
repeated because this delivery changes documentation/schema fixtures only.

## Introductory walkthrough follow-up

The maintainer accepted the proposed operation and requested an accessible
explanation for new developers, contributors and other readers. Added
[From approved software to a running robot](../guides/releases-explained.md),
linked from the root README, documentation map and release specification.
It explains release inputs, file/descriptor fingerprints, signatures, keyrings,
catalogs and separate publisher/authority/device roles. Two Mermaid diagrams
cover creation/signing/provisioning through durable acceptance, preparation,
activation, actual health and verified recovery. The guide explicitly describes
planned behavior rather than an executable workflow.

Live issue inspection on 2026-10-24 confirmed that #57 owns production lifecycle
design, #58 device enrollment, #99 device credential rotation/revocation and #100
publisher signing/metadata lifecycle. All four are deferred FUT-06 work. The guide
distinguishes these scopes and does not promise automatic publisher-key enrollment
as part of device enrollment. No issue scope or implementation was changed.

Repeated the link/fence/newline command above after adding the guide: 169 relative
links/fragments passed. Repeated configured hooks over changed/untracked files
and `git diff --check`: passed. Manually reviewed Mermaid source and diagram
branches against the release and coordination contracts; rendered diagram layout
was not inspected. No schemas, fixture bytes or runtime behavior changed in this
follow-up, so schema/vector and runtime checks were not repeated.

## Contract clarification and expanded explanation

Following maintainer review, clarified that `runtime.environment: default`
selects the release's independent Pixi workspace, rather than the repository's
root development environments. Explained the distinction between bounded ID
length, publishing conventions and rejecting conflicting immutable bindings.
Documented the 240-character relative-path and 1,024-entry local-catalog bounds
as initial enforced version 1 policies, without measured portability/capacity
claims. Resulting filesystem paths/components still need target validation;
catalog bounds do not authorize truncation or eviction of protected recovery
inputs. The values and existing rejection rules are unchanged.

Renamed the shared schema definition from `hex32` to `hex_32_bytes` and updated
its SHA-256/public-key references. Its accepted representation is still 32 raw
bytes encoded as 64 lowercase hex characters. No release descriptor, payload,
catalog or byte-vector fixture changed.

Expanded the introductory guide with a glossary, separate workspace examples,
ID/digest and catalog examples, concrete tamper cases, key-pair reuse/loss,
an eight-step deployment narrative, safe-path/canonical-byte explanations and a
fixture walkthrough. Kept the maintainer's removal of the documentation-map
introduction and their table edits intact. Diagram source was unchanged; its
previous rendered-layout limitation still applies.

Live issue inspection confirmed #13 owns catalog integrity/conflicts, #51/#65
own artifact delivery and protected cache policy, and #100 owns publisher
signing/metadata lifecycle. Also inspected #35/#37 and #74/#75/#78 to distinguish
deployment UI and central inventory scope from release publishing. No explicit
owner was found for release-ID generation conventions, a publishing UI or
catalog scaling beyond the current bound. Recorded those planning gaps in the
guide without adding scope to existing issues or creating future deliveries.

Repeated the schema/vector and relative-link commands above: five schemas,
five fixture documents, both A/B vectors, 24 schema mutations and 170 relative
links/fragments passed. Checked that all schema references use `hex_32_bytes`.
Configured hooks over changed/untracked files and `git diff --check` passed.
Runtime tests were not repeated for these schema-reference/documentation edits.

## Connected document example

Added an early teaching example to `releases-explained.md`: a protected-config
and release-directory tree followed by descriptor, signature-envelope, publisher
keyring and catalog JSON excerpts. The repeated release ID, descriptor digest
and publisher key ID connect the documents explicitly. A short reader sequence
distinguishes descriptor digest comparison, signature verification and payload
hash checks. Excerpts clearly omit required fields and use labelled symbolic
values; they are neither deployable inputs nor new cryptographic fixtures.

Checked the example relationships from the repository root with:

```sh
python3 - <<'PY'
import json
import re
from pathlib import Path
text = Path('docs/guides/releases-explained.md').read_text()
section = text.split('## One release, shown across its files\n', 1)[1]
section = section.split('## A release fixes what we mean by a software version', 1)[0]
examples = re.findall(r'```json\n(.*?)\n```', section, re.S)
assert len(examples) == 4
descriptor, signature, keyring, catalog = [json.loads(value) for value in examples]
entry = catalog['releases'][0]
assert descriptor['release_id'] == entry['release_id'] == entry['directory']
assert entry['descriptor_digest'] == signature['descriptor_digest']
key = keyring['publishers'][0]
assert descriptor['signing']['key_id'] == key['key_id']
assert descriptor['signing']['algorithm'] == key['algorithm'] == 'Ed25519'
assert descriptor['entrypoint']['argv'][1] == descriptor['files'][0]['path']
print('Four teaching JSON excerpts parse; identity, key and file references agree')
PY
```

Result: passed. Repeated the relative-link/fence/newline check: 171 relative
links/fragments passed. Configured hooks over changed/untracked files and
`git diff --check` passed. Mermaid diagrams, schemas and byte-vector fixtures
were unchanged; no runtime or cryptographic checks were added or repeated.

## Explain concepts before using them

Reworked the opening after reader feedback that the combined example introduced
signature/keyring/hash terminology before explaining it. The guide now starts
with an application A-to-B change, defines a release and descriptor, explains
file fingerprints and descriptor digests, introduces publisher key pairs and
signatures, then explains trusted keyrings and the catalog. Each JSON excerpt
follows its concept; the combined directory/verification sequence comes after
those explanations. Removed the front-loaded glossary and duplicate explanations.
No contract, schema, fixture bytes or Mermaid diagram changed.

The preceding connected-example command describes the previous four-excerpt
layout. For the current progressive six-excerpt layout, use:

```sh
python3 - <<'PY'
import json
import re
from pathlib import Path
text = Path('docs/guides/releases-explained.md').read_text()
intro = text.split('## Publisher, authority and device have separate powers', 1)[0]
examples = re.findall(r'```json\n(.*?)\n```', intro, re.S)
assert len(examples) == 6
descriptor, files, signing, signature, keyring, catalog = [json.loads(x) for x in examples]
entry = catalog['releases'][0]
assert descriptor['release_id'] == entry['release_id'] == entry['directory']
assert entry['descriptor_digest'] == signature['descriptor_digest']
key = keyring['publishers'][0]
assert signing['signing']['key_id'] == key['key_id']
assert signing['signing']['algorithm'] == key['algorithm'] == 'Ed25519'
assert descriptor['entrypoint']['argv'][1] == files['files'][0]['path']
print('Six progressive JSON excerpts parse; identity, key and file references agree')
PY
```

Result: passed. Manual reading-order review checked that hashing, publisher
keys, signatures and keyrings are explained before their JSON excerpts. Repeated
the relative-link/fence/newline command: 171 links/fragments passed. Configured
hooks over changed/untracked files and `git diff --check` passed. Runtime,
schema/vector and rendered-diagram checks were not repeated for this prose and
example-order change.

## README workflow entry point

Promoted the walkthrough from a paragraph under contributor navigation to a
highlighted callout at the start of the README's Planned MVP section. Its summary
covers creation/approval, deployment requests, preparation, execution, health and
recovery, while explicitly retaining the planned-behavior boundary. Repeated the
relative-link/fence/newline check (171 links/fragments) and `git diff --check`:
passed. No executable or diagram changes were made in this follow-up.

## 2026-10-25 — Provisioning boundaries and numbered deployment journey

Working-tree follow-up based on `bd0b4c1`. Clarified that creating a release does
not update robot catalogs: trusted MVP setup supplies inputs and entries only to
robots that need the release. Existing trusted publisher keys can verify further
releases. The walkthrough distinguishes scriptable administration from FleetForge
artifact delivery and links its future design/implementation owners (#51/#64),
whose live scope was inspected during the explanation. The release contract and
future artifact architecture now identify the catalog-registration boundary that
remote delivery must specify, including interruption and ID/digest conflicts.

Condensed the journey diagram into eight numbered stages, each with a short
description matching the retained detailed list. Explained directory access,
symbolic links, replacement between verification and use, and the ownership and
operating-system protections required by the existing safe-path contract.

Repeated the relative-link/fence/newline and progressive-example commands above:
26 links/fragments across the changed documents passed; all six JSON excerpts
still parse and agree. Configured pre-commit hooks over these four changed
documents and `git diff --check` passed. Manually reviewed the Mermaid source
against the eight prose steps; rendered layout was not inspected. Schemas,
fixture bytes and executable behavior are unchanged, so runtime, cryptographic
and schema/vector checks were not repeated.

## 2026-10-25 — Granular journey diagrams and visual cues

Working-tree follow-up based on the maintainer's amended commit `3e03b3c`.
Expanded the journey from eight combined stages to 26 numbered actions across
five diagrams: publishing, trusted provisioning, request/acceptance, release
verification/preparation, and activation/reporting. The adjacent numbered prose
matches each diagram. Separate actions now include locking/testing/signing,
supplying release/package bytes and catalog entries, durable authority/robot
records, acknowledgement, individual verification stages, stop/start, health,
and recording/synchronizing/displaying observations. The existing failure and
recovery diagram remains the detailed branch from the successful path.

Reviewed the official [Mermaid flowchart documentation](https://mermaid.js.org/syntax/flowchart.html)
on 2026-10-25. Dedicated icon/image shapes require renderer support, and icon
shapes require registered icon packs. Used Unicode visual cues beside complete
text labels and standard flowchart shapes, including cylinders for durable
records. No external image resources, renderer configuration or dependencies
were introduced. Glyph appearance depends on the viewer's fonts.

Check diagram/prose numbering from the repository root:

```sh
python3 - <<'PY'
from pathlib import Path
import re
text = Path('docs/guides/releases-explained.md').read_text()
journey = text.split('## The complete journey to the robot\n', 1)[1]
journey = journey.split('### What can fail, and what stays running?', 1)[0]
diagrams = re.findall(r'```mermaid\n(.*?)\n```', journey, re.S)
assert len(diagrams) == 5
labels = re.findall(r'"[^"\n]*?\b(\d+)\. ', '\n'.join(diagrams))
paragraphs = re.findall(r'^(\d+)\. \*\*', journey, re.M)
assert list(map(int, labels)) == list(range(1, 27))
assert labels == paragraphs
print('Five diagrams and 26 ordered diagram/prose steps agree')
PY
```

Manual source review checked that the split preserves trust, durable acceptance,
preparation-before-switch, health and recovery boundaries. Rendered diagram
layout was not inspected; the maintainer will review the visual result. The
relative-link/fence/newline check, progressive JSON example check, numbering
check, configured documentation hooks and `git diff --check` passed. No schemas,
fixture bytes or runtime behavior changed.

## 2026-10-25 — Explain participants and responsibility handoffs

Refined the same working-tree follow-up after reader feedback. The walkthrough
now distinguishes publisher approval, operator choice, authority authorization
and requested state, and agent execution and observed state. It explains trusted
setup, Pixi, application/probe and console responsibilities, with an example of
requested release B while release A is still observed. Each phase names its
owner; Mermaid groups expose the operator-to-authority-to-agent handoff and the
separate managed application and console. Numbered prose uses explicit subjects
to distinguish the agent invoking tools from those tools deciding deployment
policy. Preserved the maintainer's intervening prose and table edits.

Compared the explanation with the existing architecture/security owners. Checked
the latest official Pixi install reference and local Pixi 0.83.0 against the
repository's `>=0.83.0` requirement for the limited environment-installation
description; no package configuration or CLI behavior changed. The existing
relative-link/fence/newline, six-example and 26-step numbering checks and
`git diff --check` passed. Configured documentation hooks passed. Reviewed
Mermaid source; rendered layout was not inspected. This clarification changes
neither the release contract nor executable behavior.
