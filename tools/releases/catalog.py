"""Bounded publisher/integrity checks and local fixture provisioning.

Publisher verification is required by the CLI unless integrity-only is explicit.
"""

import argparse
from collections.abc import Iterator
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMAS = Path(__file__).resolve().parents[2] / "schemas/releases/v1"
# Version 1 input policy; docs/specs/releases.md owns these limits.
MAX_DESCRIPTOR_BYTES = 1024 * 1024
MAX_CATALOG_BYTES = 1024 * 1024
MAX_SIGNATURE_BYTES = 4 * 1024
MAX_FILE_BYTES = 1024**3
MAX_PAYLOAD_BYTES = 4 * 1024**3
MAX_PAYLOAD_FILES = 4096
MAX_PATH_CHARS = 240
MAX_JSON_DEPTH = 16
# A one-character segment plus a slash needs two characters, except the last.
MAX_PATH_SEGMENTS = (MAX_PATH_CHARS + 1) // 2
# Loose bound: every payload may have its own parents, plus two metadata files.
MAX_TREE_ENTRIES = MAX_PAYLOAD_FILES * MAX_PATH_SEGMENTS + 2
MAX_SNAPSHOT_BYTES = MAX_PAYLOAD_BYTES + MAX_DESCRIPTOR_BYTES + MAX_SIGNATURE_BYTES
# Implementation budgets, independent of the release format.
COPY_CHUNK_BYTES = 64 * 1024
LOCK_CHECK_TIMEOUT_SECONDS = 60
# Largest integer for which all consecutive values remain exact in IEEE-754 binary64.
MAX_SAFE_JSON_INTEGER = 2**53 - 1
PATH = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._-]*(/[A-Za-z0-9_][A-Za-z0-9._-]*)*\Z")


class ReleaseError(ValueError):
    """A bounded, classified failure before any install or execution."""

    def __init__(self, code: str, context: str) -> None:
        super().__init__(f"{code}: {context}")
        self.code = code


def require(ok: bool, context: str, code: str = "release_invalid") -> None:
    if not ok:
        raise ReleaseError(code, context)


def path(value: str) -> None:
    require(
        len(value) <= MAX_PATH_CHARS and PATH.fullmatch(value) is not None,
        "unsafe path",
    )


def canonical(value: Any) -> bytes:
    """JCS encoding for the contract's integer-only JSON domain.

    Integers stay in the IEEE-754 exact range; keys sort by UTF-16 code units.
    Floats and lone surrogates reject rather than receive approximate encoding.
    """
    if isinstance(value, dict):
        value = dict(
            sorted(value.items(), key=lambda item: item[0].encode("utf-16-be"))
        )
        return (
            b"{"
            + b",".join(canonical(k) + b":" + canonical(v) for k, v in value.items())
            + b"}"
        )
    if isinstance(value, list):
        return b"[" + b",".join(map(canonical, value)) + b"]"
    require(not isinstance(value, float), "non-integer number")
    if type(value) is int:
        require(
            abs(value) <= MAX_SAFE_JSON_INTEGER,
            "integer outside interoperable JSON range",
        )
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def parse(data: bytes) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, "duplicate JSON member")
            result[key] = value
        return result

    # Bound nesting before invoking the JSON decoder (strings may contain brackets).
    depth = 0
    quoted = escaped = False
    for byte in data:
        if quoted:
            if escaped:
                escaped = False
            elif byte == ord("\\"):
                escaped = True
            elif byte == ord('"'):
                quoted = False
        elif byte == ord('"'):
            quoted = True
        elif byte in b"[{":
            depth += 1
            require(depth <= MAX_JSON_DEPTH, f"JSON nesting exceeds {MAX_JSON_DEPTH}")
        elif byte in b"]}":
            depth -= 1
    try:
        result = json.loads(data.decode("utf-8"), object_pairs_hook=pairs)
        canonical(result)  # Reject invalid Unicode and non-integer numbers everywhere.
        return result
    except (UnicodeError, ValueError, RecursionError) as error:
        if isinstance(error, ReleaseError):
            raise
        raise ReleaseError("release_invalid", "malformed JSON") from error


def schema(value: Any, name: str) -> None:
    registry: Registry[Any] = Registry().with_resources(
        (p.name, Resource.from_contents(json.loads(p.read_bytes())))
        for p in SCHEMAS.glob("*.schema.json")
    )
    validator = Draft202012Validator(
        json.loads((SCHEMAS / name).read_bytes()), registry=registry
    )
    require(validator.is_valid(value), f"{name}: schema mismatch")


@contextmanager
def directory(root: Path) -> Iterator[int]:
    """Open every ancestor with no-follow handles, including the configured root."""
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in root.absolute().parts[1:]:
            require(part not in (".", ".."), "unsafe root")
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd
            )
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def read(fd: int, name: str, maximum: int) -> bytes:
    with os.fdopen(
        os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd), "rb"
    ) as stream:
        info = os.fstat(stream.fileno())
        require(
            stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
            "nonregular or hard-linked input",
        )
        require(info.st_size <= maximum, "input size limit")
        data = stream.read(maximum + 1)
        require(len(data) <= maximum, "input grew past size limit")
        return data


def snapshot(
    fd: int, target: Path, prefix: str = "", budget: list[int] | None = None
) -> None:
    """Copy through pinned handles; never traverse symlinks or block on special files."""
    if budget is None:
        budget = [0, 0]  # Shared entry count and copied-byte count across recursion.
    with os.scandir(fd) as entries:
        names = []
        for entry in entries:
            names.append(entry.name)
            require(len(names) <= MAX_TREE_ENTRIES, "too many directory entries")
    for name in names:
        relative = prefix + name
        path(relative)
        budget[0] += 1
        require(budget[0] <= MAX_TREE_ENTRIES, "too many directory entries")
        info = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if stat.S_ISDIR(info.st_mode):
            target.joinpath(name).mkdir()
            child = os.open(
                name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd
            )
            try:
                snapshot(child, target / name, relative + "/", budget)
            finally:
                os.close(child)
        else:
            maximum = (
                MAX_DESCRIPTOR_BYTES
                if relative == "release.json"
                else MAX_SIGNATURE_BYTES
                if relative == "release.sig.json"
                else MAX_FILE_BYTES
            )
            with os.fdopen(
                os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd),
                "rb",
            ) as source:
                info = os.fstat(source.fileno())
                require(
                    stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                    "nonregular or hard-linked input",
                )
                require(info.st_size <= maximum, "file too large")
                count = 0
                with (target / name).open("xb") as output:
                    while chunk := source.read(COPY_CHUNK_BYTES):
                        count += len(chunk)
                        budget[1] += len(chunk)
                        require(
                            count <= maximum and budget[1] <= MAX_SNAPSHOT_BYTES,
                            "payload size limit",
                        )
                        output.write(chunk)


def validate(
    root: Path,
    pixi: str,
    expected: tuple[str, str] | None = None,
    *,
    keyring: Path | None,
) -> tuple[str, str]:
    data = (root / "release.json").read_bytes()
    descriptor = parse(data)
    require(isinstance(descriptor, dict), "descriptor must be an object")
    for key, supported in [("schema_version", 1), ("platform", "linux-64")]:
        require(descriptor.get(key) == supported, key, "release_unsupported")
    require(
        descriptor.get("runtime")
        == {"environment": "default", "minimum_pixi_version": "0.83.0"},
        "runtime",
        "release_unsupported",
    )
    signing = descriptor.get("signing")
    require(isinstance(signing, dict), "signing must be an object")
    require(signing.get("algorithm") == "Ed25519", "algorithm", "release_unsupported")
    schema(descriptor, "release.schema.json")
    require(canonical(descriptor) == data, "noncanonical descriptor")
    identity = (descriptor["release_id"], "sha256:" + hashlib.sha256(data).hexdigest())
    require(
        expected is None or identity == expected,
        "catalog descriptor mismatch",
        "release_integrity",
    )
    if keyring is not None:
        from tools.releases.trust import verify

        verify(root, data, signing["key_id"], keyring)
    files = descriptor["files"]
    names = [item["path"] for item in files]
    require(names == sorted(set(names)), "unordered or duplicate payload paths")
    require(
        "pixi.toml" in names and "pixi.lock" in names, "missing manifest/lock entry"
    )
    require(
        not {"release.json", "release.sig.json"} & set(names),
        "metadata in payload list",
    )
    require(
        sum(item["size"] for item in files) <= MAX_PAYLOAD_BYTES,
        "aggregate payload limit",
    )
    expected_files = set(names) | {"release.json"}
    if (root / "release.sig.json").exists():
        expected_files.add("release.sig.json")
    expected_dirs = {
        str(parent)
        for name in names
        for parent in Path(name).parents
        if str(parent) != "."
    }
    actual_files = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    actual_dirs = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_dir()}
    require(
        expected_files <= actual_files and expected_dirs <= actual_dirs,
        "missing release entry",
        "release_unavailable",
    )
    require(
        actual_files == expected_files and actual_dirs == expected_dirs,
        "unexpected or missing release entries",
        "release_integrity",
    )
    for item in files:
        path(item["path"])
        payload = root / item["path"]
        with payload.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        require(
            payload.stat().st_size == item["size"] and digest == item["sha256"],
            "payload mismatch: " + item["path"],
            "release_integrity",
        )
    for command in [descriptor["entrypoint"], descriptor["health"]]:
        require((root / command["cwd"]).is_dir(), "missing cwd")
    health = descriptor["health"]
    require(
        max(health["probe_timeout_ms"], health["interval_ms"])
        <= health["startup_timeout_ms"],
        "health timing",
    )
    manifest = tomllib.loads((root / "pixi.toml").read_text())
    require(
        isinstance(manifest.get("dependencies", {}), dict)
        and isinstance(manifest.get("workspace"), dict),
        "manifest structure",
    )
    require(
        set(manifest) <= {"workspace", "dependencies"},
        "adapter supports only binary Conda manifests",
        "release_unsupported",
    )
    require(
        all(isinstance(v, str) for v in manifest.get("dependencies", {}).values()),
        "adapter requires string Conda dependencies",
        "release_unsupported",
    )
    require(
        manifest.get("workspace", {}).get("platforms") == ["linux-64"],
        "manifest platform",
        "release_integrity",
    )
    # Pixi inspects only the verified disposable inputs, never source directories.
    result = subprocess.run(
        [
            pixi,
            "lock",
            "--check",
            "--offline",
            "--no-config",
            "--manifest-path",
            str(root / "pixi.toml"),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=LOCK_CHECK_TIMEOUT_SECONDS,
    )
    require(
        result.returncode == 0,
        "manifest/lock consistency failed (Pixi lock --check --offline)",
        "release_integrity",
    )
    verify_input_hash(root, files, "pixi.lock")
    verify_input_hash(root, files, "pixi.toml")
    return identity


def verify_input_hash(root: Path, files: list[Any], name: str) -> None:
    data = (root / name).read_bytes()
    item = next(item for item in files if item["path"] == name)
    require(
        hashlib.sha256(data).hexdigest() == item["sha256"],
        "source lock changed",
        "release_integrity",
    )


def catalog(fd: int) -> dict[str, Any]:
    value = parse(read(fd, "catalog.json", MAX_CATALOG_BYTES))
    require(isinstance(value, dict), "catalog must be an object")
    assert isinstance(value, dict)
    require(value.get("schema_version") == 1, "catalog version", "release_unsupported")
    schema(value, "catalog.schema.json")
    entries = value["releases"]
    ids = [e["release_id"] for e in entries]
    directories = [e["directory"] for e in entries]
    require(len(ids) == len(set(ids)), "duplicate catalog ID", "release_conflict")
    require(ids == sorted(ids), "catalog ordering")
    require(len(directories) == len(set(directories)), "aliased directories")
    require(
        not any(
            a != b and b.startswith(a + "/") for a in directories for b in directories
        ),
        "nested release directories",
    )
    return value


def check(
    root: Path,
    pixi: str,
    requested: str | None = None,
    digest: str | None = None,
    *,
    keyring: Path | None,
) -> dict[str, Any]:
    with directory(root) as fd:
        value = catalog(fd)
    selected = [
        e
        for e in value["releases"]
        if requested is None or e["release_id"] == requested
    ]
    require(
        bool(selected) or requested is None,
        "unknown requested ID",
        "release_unavailable",
    )
    for entry in selected:
        require(
            digest is None or digest == entry["descriptor_digest"],
            "requested digest conflicts",
            "release_conflict",
        )
        with tempfile.TemporaryDirectory() as temporary:
            with directory(root / entry["directory"]) as release_fd:
                snapshot(release_fd, Path(temporary))
            validate(
                Path(temporary),
                pixi,
                (entry["release_id"], entry["descriptor_digest"]),
                keyring=keyring,
            )
    return value


def provision(
    source: Path, destination: Path, pixi: str, *, keyring: Path | None
) -> dict[str, Any]:
    """Publish a complete deterministic fixture tree, or verify an identical tree.

    Destination parent must be provisioner-owned. Concurrent writers are unsupported.
    Existing destinations are never overwritten, including incomplete failed setups.
    """
    with directory(destination.parent):
        pass
    with tempfile.TemporaryDirectory(
        prefix=".fleetforge-", dir=destination.parent
    ) as temporary:
        stage = Path(temporary) / "inputs"
        stage.mkdir()
        entries = []
        for name in ["ros-counter-a-v1", "ros-counter-b-v1"]:
            copied = stage / name
            copied.mkdir()
            with directory(source / name) as fd:
                snapshot(fd, copied)
            identity = validate(copied, pixi, keyring=keyring)
            entries.append(
                dict(
                    release_id=identity[0],
                    descriptor_digest=identity[1],
                    directory=name,
                )
            )
        value = dict(
            schema_version=1, releases=sorted(entries, key=lambda e: e["release_id"])
        )
        schema(value, "catalog.schema.json")
        (stage / "catalog.json").write_bytes(canonical(value))
        with directory(stage) as stage_fd:
            catalog(stage_fd)
        if destination.exists() or destination.is_symlink():
            existing = check(destination, pixi, keyring=keyring)
            require(
                existing == value,
                "existing catalog binding differs",
                "release_conflict",
            )
        else:
            stage.rename(destination)
        return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "provision"])
    parser.add_argument("root", type=Path)
    parser.add_argument("--source", type=Path, default=Path("examples/releases"))
    parser.add_argument("--release-id")
    parser.add_argument("--digest")
    trust = parser.add_mutually_exclusive_group(required=True)
    trust.add_argument("--keyring", type=Path)
    trust.add_argument("--integrity-only", action="store_true")
    args = parser.parse_args()
    try:
        pixi = shutil.which("pixi")
        require(pixi is not None, "host Pixi missing")
        assert pixi is not None
        require(
            args.digest is None or args.release_id is not None,
            "--digest requires --release-id",
        )
        value = (
            provision(args.source, args.root, pixi, keyring=args.keyring)
            if args.action == "provision"
            else check(
                args.root, pixi, args.release_id, args.digest, keyring=args.keyring
            )
        )
        print(json.dumps({"integrity_only": args.integrity_only, "catalog": value}))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        code = (
            "release_unavailable"
            if isinstance(error, FileNotFoundError)
            else "release_invalid"
        )
        print(
            str(error)
            if isinstance(error, ReleaseError)
            else f"{code}: input access or validation failed",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
