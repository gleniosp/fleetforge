"""Integrity boundary regressions using real files and the installed Pixi."""

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from tools.releases.catalog import (
    ReleaseError,
    canonical,
    check,
    parse,
    provision,
)

SOURCE = Path(__file__).resolve().parents[2] / "releases"
PIXI = shutil.which("pixi") or "pixi"


def fingerprints(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }


@pytest.fixture
def tmp_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    # macOS may expose its host temporary directory through /var or /tmp links.
    # Configure the physical owned root explicitly; release paths still reject links.
    return tmp_path_factory.mktemp("release-integrity").resolve()


@pytest.fixture
def inputs(tmp_path: Path) -> Path:
    root = tmp_path / "inputs"
    provision(SOURCE, root, PIXI)
    return root


def test_repeatable_and_read_only(inputs: Path, tmp_path: Path) -> None:
    before = fingerprints(SOURCE)
    copy_before = fingerprints(inputs)
    value = check(inputs, PIXI)
    assert provision(SOURCE, inputs, PIXI) == value
    assert provision(SOURCE, tmp_path / "another", PIXI) == value
    assert fingerprints(inputs) == copy_before
    assert fingerprints(SOURCE) == before
    assert not list(inputs.rglob(".pixi"))


@pytest.mark.parametrize(
    "data",
    [
        b'{"a":1,"a":2}',
        b'{"a":NaN}',
        b'{"a":1.5}',
        b'{"a":"\\ud800"}',
        b"[" * 17 + b"0" + b"]" * 17,
        b'{"a":9007199254740992}',
    ],
)
def test_strict_json(data: bytes) -> None:
    with pytest.raises(ReleaseError):
        parse(data)


@pytest.mark.parametrize(
    "mutation",
    [
        "tamper",
        "extra",
        "missing",
        "symlink",
        "hardlink",
        "fifo",
        "directory_link",
        "noncanonical",
        "unknown_field",
        "timing",
        "unsafe_path",
        "duplicate_path",
        "unsupported",
    ],
)
def test_reject_release(inputs: Path, mutation: str, tmp_path: Path) -> None:
    root = inputs / "ros-counter-a-v1"
    payload = root / "app/main.py"
    descriptor = json.loads((root / "release.json").read_bytes())
    if mutation == "tamper":
        payload.write_text("tampered")
    elif mutation == "extra":
        (root / "extra").write_text("extra")
    elif mutation == "missing":
        payload.unlink()
    elif mutation in {"symlink", "hardlink", "fifo"}:
        payload.unlink()
        if mutation == "symlink":
            payload.symlink_to(tmp_path / "missing")
        elif mutation == "hardlink":
            payload.hardlink_to(root / "app/health.py")
        else:
            import os

            os.mkfifo(payload)
    elif mutation == "directory_link":
        (root / "outside").symlink_to(tmp_path, target_is_directory=True)
    elif mutation == "noncanonical":
        (root / "release.json").write_bytes(canonical(descriptor) + b"\n")
    else:
        if mutation == "unknown_field":
            descriptor["extra"] = True
        elif mutation == "timing":
            descriptor["health"]["startup_timeout_ms"] = 1
        elif mutation == "unsafe_path":
            descriptor["files"][0]["path"] = "../outside"
        elif mutation == "duplicate_path":
            descriptor["files"].append(descriptor["files"][0])
        else:
            descriptor["platform"] = "linux-aarch64"
        (root / "release.json").write_bytes(canonical(descriptor))
    if mutation not in {
        "tamper",
        "extra",
        "missing",
        "symlink",
        "hardlink",
        "fifo",
        "directory_link",
    }:
        catalog = json.loads((inputs / "catalog.json").read_bytes())
        catalog["releases"][0]["descriptor_digest"] = (
            "sha256:" + hashlib.sha256((root / "release.json").read_bytes()).hexdigest()
        )
        (inputs / "catalog.json").write_bytes(canonical(catalog))
    with pytest.raises((ReleaseError, OSError)):
        check(inputs, PIXI)


def test_catalog_failures(inputs: Path) -> None:
    original = (inputs / "catalog.json").read_bytes()
    with pytest.raises(ReleaseError, match="release_unavailable"):
        check(inputs, PIXI, "unknown")
    with pytest.raises(ReleaseError, match="release_conflict"):
        check(inputs, PIXI, "ros-counter-a-v1", "sha256:" + "0" * 64)
    for field, value in [
        ("directory", "../escape"),
        ("descriptor_digest", "sha256:" + "0" * 64),
        ("extra", True),
    ]:
        catalog = json.loads(original)
        catalog["releases"][0][field] = value
        (inputs / "catalog.json").write_bytes(canonical(catalog))
        with pytest.raises(ReleaseError):
            check(inputs, PIXI)
    catalog = json.loads(original)
    catalog["releases"].append(catalog["releases"][0])
    (inputs / "catalog.json").write_bytes(canonical(catalog))
    with pytest.raises(ReleaseError, match="release_conflict"):
        check(inputs, PIXI)


def test_lock_drift_without_repair(tmp_path: Path) -> None:
    source = tmp_path / "source"
    shutil.copytree(SOURCE, source)
    release = source / "ros-counter-a-v1"
    manifest = release / "pixi.toml"
    manifest.write_text(manifest.read_text().replace("=3.14.10", "=0.0.1"))
    data = json.loads((release / "release.json").read_bytes())
    for item in data["files"]:
        if item["path"] == "pixi.toml":
            item["size"] = manifest.stat().st_size
            item["sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
    (release / "release.json").write_bytes(canonical(data))
    before = fingerprints(source)
    with pytest.raises(ReleaseError, match="manifest/lock consistency"):
        provision(source, tmp_path / "destination", PIXI)
    assert fingerprints(source) == before
    assert not (tmp_path / "destination").exists()


def test_conflicting_existing_binding(inputs: Path, tmp_path: Path) -> None:
    source = tmp_path / "source"
    shutil.copytree(SOURCE, source)
    release = source / "ros-counter-a-v1/release.json"
    data = json.loads(release.read_bytes())
    data["signing"]["key_id"] = "another-publisher"
    release.write_bytes(canonical(data))
    before = fingerprints(inputs)
    with pytest.raises(ReleaseError, match="release_conflict"):
        provision(source, inputs, PIXI)
    assert fingerprints(inputs) == before


def test_wrong_binding_rejects_before_pixi(
    inputs: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail("Pixi must not run for a descriptor/catalog mismatch")

    monkeypatch.setattr("tools.releases.catalog.subprocess.run", forbidden)
    value = json.loads((inputs / "catalog.json").read_bytes())
    value["releases"][0]["descriptor_digest"] = "sha256:" + "0" * 64
    (inputs / "catalog.json").write_bytes(canonical(value))
    with pytest.raises(ReleaseError, match="catalog descriptor mismatch"):
        check(inputs, PIXI)


def test_root_link_and_catalog_limit(inputs: Path, tmp_path: Path) -> None:
    link = tmp_path / "linked"
    link.symlink_to(inputs, target_is_directory=True)
    with pytest.raises(OSError):
        check(link, PIXI)
    (inputs / "catalog.json").write_bytes(b" " * (1024 * 1024 + 1))
    with pytest.raises(ReleaseError, match="size limit"):
        check(inputs, PIXI)
