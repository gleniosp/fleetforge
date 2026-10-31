"""Local publisher trust and disposable host signing tools."""

import argparse
import hashlib
import os
from pathlib import Path
import sys

from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from tools.releases.catalog import (
    MAX_CATALOG_BYTES,
    MAX_DESCRIPTOR_BYTES,
    MAX_SIGNATURE_BYTES,
    ReleaseError,
    canonical,
    directory,
    parse,
    read,
    require,
    schema,
)


def signature_message(descriptor: bytes) -> bytes:
    return b"FleetForge.release.v1\0" + descriptor


def load_keyring(source: Path) -> dict[str, Ed25519PublicKey]:
    with directory(source.absolute().parent) as fd:
        value = parse(read(fd, source.name, MAX_CATALOG_BYTES))
    schema(value, "keyring.schema.json")
    keys = {}
    for entry in value["publishers"]:
        key_id = entry["key_id"]
        require(key_id not in keys, "duplicate publisher ID")
        try:
            keys[key_id] = Ed25519PublicKey.from_public_bytes(
                bytes.fromhex(entry["public_key"])
            )
        except (ValueError, UnsupportedAlgorithm) as error:
            raise ReleaseError(
                "release_untrusted_publisher", "invalid public key"
            ) from error
    return keys


def verify(root: Path, data: bytes, key_id: str, keyring: Path) -> None:
    try:
        with directory(root) as fd:
            envelope = parse(read(fd, "release.sig.json", MAX_SIGNATURE_BYTES))
    except FileNotFoundError as error:
        raise ReleaseError(
            "release_untrusted_publisher", "missing signature"
        ) from error
    schema(envelope, "signature.schema.json")
    require(
        envelope["descriptor_digest"] == "sha256:" + hashlib.sha256(data).hexdigest(),
        "signature envelope digest mismatch",
        "release_integrity",
    )
    keys = load_keyring(keyring)
    require(key_id in keys, "unknown publisher", "release_untrusted_publisher")
    try:
        keys[key_id].verify(
            bytes.fromhex(envelope["signature"]), signature_message(data)
        )
    except (InvalidSignature, UnsupportedAlgorithm) as error:
        raise ReleaseError(
            "release_untrusted_publisher", "invalid signature"
        ) from error


def generate(destination: Path, key_id: str) -> None:
    """Create a new private host directory; never overwrite existing secrets."""
    key = Ed25519PrivateKey.generate()
    keyring = {
        "schema_version": 1,
        "publishers": [
            {
                "key_id": key_id,
                "algorithm": "Ed25519",
                "public_key": key.public_key().public_bytes_raw().hex(),
            }
        ],
    }
    schema(keyring, "keyring.schema.json")
    destination.mkdir(mode=0o700)
    with (destination / "publisher.key").open("xb") as output:
        os.fchmod(output.fileno(), 0o600)
        output.write(key.private_bytes_raw())
    (destination / "keyring.json").write_bytes(canonical(keyring))


def sign(root: Path, private_key: Path, keyring: Path) -> None:
    """Sign existing canonical bytes without changing descriptor identity."""
    with directory(root) as fd:
        data = read(fd, "release.json", MAX_DESCRIPTOR_BYTES)
    descriptor = parse(data)
    schema(descriptor, "release.schema.json")
    require(canonical(descriptor) == data, "noncanonical descriptor")
    with directory(private_key.absolute().parent) as fd:
        secret = read(fd, private_key.name, 32)
    key = Ed25519PrivateKey.from_private_bytes(secret)
    keys = load_keyring(keyring)
    key_id = descriptor["signing"]["key_id"]
    require(key_id in keys, "unknown publisher", "release_untrusted_publisher")
    require(
        keys[key_id].public_bytes_raw() == key.public_key().public_bytes_raw(),
        "private key does not match publisher binding",
        "release_untrusted_publisher",
    )
    envelope = {
        "schema_version": 1,
        "descriptor_digest": "sha256:" + hashlib.sha256(data).hexdigest(),
        "signature": key.sign(signature_message(data)).hex(),
    }
    with (root / "release.sig.json").open("xb") as output:
        output.write(canonical(envelope))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["generate", "sign"])
    parser.add_argument("root", type=Path)
    parser.add_argument("--key-id", default="demo-publisher-1")
    parser.add_argument("--private-key", type=Path)
    parser.add_argument("--keyring", type=Path)
    args = parser.parse_args()
    try:
        if args.action == "generate":
            generate(args.root, args.key_id)
        else:
            require(
                args.private_key is not None and args.keyring is not None,
                "sign requires --private-key and --keyring",
            )
            sign(args.root, args.private_key, args.keyring)
    except (OSError, ValueError, UnsupportedAlgorithm) as error:
        print(
            str(error)
            if isinstance(error, ReleaseError)
            else "signing input or output failed",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
