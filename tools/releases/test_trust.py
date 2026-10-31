"""Publisher conformance and trust rejection before Pixi invocation."""

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from tools.releases.catalog import ReleaseError, canonical, check, provision
from tools.releases.trust import generate, load_keyring, sign, signature_message

REPO = Path(__file__).resolve().parents[2]
PIXI = shutil.which("pixi") or "pixi"


@pytest.fixture
def signed(tmp_path: Path) -> tuple[Path, Path, Path]:
    tmp_path = tmp_path.resolve()
    secrets = tmp_path / "secrets"
    generate(secrets, "unsigned-demo-publisher")
    source = tmp_path / "source"
    shutil.copytree(REPO / "examples/releases", source)
    keyring = secrets / "keyring.json"
    for release in [source / "ros-counter-a-v1", source / "ros-counter-b-v1"]:
        sign(release, secrets / "publisher.key", keyring)
    destination = tmp_path / "catalog"
    provision(source, destination, PIXI, keyring=keyring)
    return destination, keyring, secrets


def test_shared_vectors() -> None:
    fixtures = REPO / "examples/releases/conformance/v1"
    vectors = json.loads((fixtures / "vectors.json").read_bytes())
    for name, vector in vectors.items():
        descriptor = json.loads((fixtures / f"release-{name}.json").read_bytes())
        encoded = canonical(descriptor)
        assert encoded.hex() == vector["canonical_utf8_hex"]
        assert (
            "sha256:" + hashlib.sha256(encoded).hexdigest()
            == vector["descriptor_digest"]
        )
        assert signature_message(encoded).hex() == vector["signature_message_hex"]


def test_signed_ab_read_only(signed: tuple[Path, Path, Path]) -> None:
    root, keyring, _ = signed
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert len(check(root, PIXI, keyring=keyring)["releases"]) == 2
    assert all(p.read_bytes() == data for p, data in before.items())
    assert not list(root.rglob(".pixi"))


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "bad",
        "substitute",
        "unknown",
        "wrong",
        "modified",
        "encoding",
        "payload",
    ],
)
def test_reject_before_pixi(
    signed: tuple[Path, Path, Path], mutation: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, keyring, secrets = signed
    release = root / "ros-counter-a-v1"
    signature = release / "release.sig.json"
    envelope = json.loads(signature.read_bytes())
    if mutation == "missing":
        signature.unlink()
    elif mutation == "bad":
        envelope["signature"] = "00" * 64
        signature.write_bytes(canonical(envelope))
    elif mutation == "substitute":
        signature.write_bytes((root / "ros-counter-b-v1/release.sig.json").read_bytes())
    elif mutation in {"unknown", "wrong"}:
        if mutation == "unknown":
            keyring.write_bytes(canonical({"schema_version": 1, "publishers": []}))
        else:
            generate(secrets.parent / "wrong", "unsigned-demo-publisher")
            keyring.write_bytes((secrets.parent / "wrong/keyring.json").read_bytes())
    elif mutation == "modified":
        descriptor = json.loads((release / "release.json").read_bytes())
        descriptor["health"]["expected_behavior"] = "changed"
        data = canonical(descriptor)
        (release / "release.json").write_bytes(data)
        catalog = json.loads((root / "catalog.json").read_bytes())
        digest = "sha256:" + hashlib.sha256(data).hexdigest()
        catalog["releases"][0]["descriptor_digest"] = digest
        (root / "catalog.json").write_bytes(canonical(catalog))
        envelope["descriptor_digest"] = digest
        signature.write_bytes(canonical(envelope))
    elif mutation == "encoding":
        envelope["signature"] = "FF" * 64
        signature.write_bytes(canonical(envelope))
    else:
        (release / "app/main.py").write_text("tampered")

    def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail("untrusted or corrupt release reached Pixi")

    monkeypatch.setattr("tools.releases.catalog.subprocess.run", forbidden)
    with pytest.raises(ReleaseError):
        check(root, PIXI, keyring=keyring)


def test_duplicate_key_ids_reject(signed: tuple[Path, Path, Path]) -> None:
    _, keyring, _ = signed
    value = json.loads(keyring.read_bytes())
    value["publishers"] *= 2
    keyring.write_bytes(canonical(value))
    with pytest.raises(ReleaseError, match="duplicate publisher"):
        load_keyring(keyring)


@pytest.mark.parametrize(
    "mutation", ["algorithm", "encoding", "unknown_field", "duplicate"]
)
def test_invalid_keyring(signed: tuple[Path, Path, Path], mutation: str) -> None:
    _, keyring, _ = signed
    value = json.loads(keyring.read_bytes())
    if mutation == "algorithm":
        value["publishers"][0]["algorithm"] = "Ed25519ph"
    elif mutation == "encoding":
        value["publishers"][0]["public_key"] = "00"
    elif mutation == "unknown_field":
        value["publishers"][0]["url"] = "https://example.invalid/key"
    else:
        keyring.write_bytes(b'{"schema_version":1,"schema_version":1,"publishers":[]}')
    if mutation != "duplicate":
        keyring.write_bytes(canonical(value))
    with pytest.raises(ReleaseError):
        load_keyring(keyring)


def test_no_overwrite_and_private_permissions(signed: tuple[Path, Path, Path]) -> None:
    root, keyring, secrets = signed
    assert secrets.stat().st_mode & 0o777 == 0o700
    assert (secrets / "publisher.key").stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError):
        generate(secrets, "unsigned-demo-publisher")
    with pytest.raises(FileExistsError):
        sign(root / "ros-counter-a-v1", secrets / "publisher.key", keyring)
    provision(root, root, PIXI, keyring=keyring)


def test_cli_trust_is_explicit(signed: tuple[Path, Path, Path]) -> None:
    import subprocess
    import sys

    root, keyring, _ = signed
    command = [sys.executable, "-B", "-m", "tools.releases.catalog", "check", str(root)]
    result = subprocess.run(command, capture_output=True, check=False)
    assert result.returncode == 2
    result = subprocess.run(
        command + ["--keyring", str(keyring)], capture_output=True, check=True
    )
    assert json.loads(result.stdout)["integrity_only"] is False


def test_failed_provision_publishes_nothing(signed: tuple[Path, Path, Path]) -> None:
    root, keyring, _ = signed
    (root / "ros-counter-a-v1/release.sig.json").unlink()
    target = root.parent / "rejected"
    with pytest.raises(ReleaseError, match="missing signature"):
        provision(root, target, PIXI, keyring=keyring)
    assert not target.exists()


def test_signing_cli(tmp_path: Path) -> None:
    import subprocess
    import sys

    tmp_path = tmp_path.resolve()
    secrets = tmp_path / "secrets"
    release = tmp_path / "release"
    shutil.copytree(REPO / "examples/releases/ros-counter-a-v1", release)
    command = [sys.executable, "-B", "-m", "tools.releases.trust"]
    subprocess.run(command + ["generate", str(secrets)], check=True)
    subprocess.run(
        command
        + [
            "sign",
            str(release),
            "--private-key",
            str(secrets / "publisher.key"),
            "--keyring",
            str(secrets / "keyring.json"),
        ],
        check=True,
    )
    from tools.releases.catalog import validate

    validate(release, PIXI, keyring=secrets / "keyring.json")
