"""Static agent format vectors; these checks do not implement an updater."""

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator
import pytest

from tools.json_encoding import canonical

REPO = Path(__file__).resolve().parents[2]
SCHEMAS = REPO / "schemas/agent-releases/v1"
VECTORS = json.loads(
    (REPO / "examples/agent-releases/conformance/v1/vectors.json").read_bytes()
)


@pytest.mark.parametrize("vector", VECTORS, ids=lambda v: v["name"])
def test_fixed_agent_vectors(vector: dict[str, Any]) -> None:
    schema = json.loads((SCHEMAS / f"{vector['schema']}.schema.json").read_bytes())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    validator.validate(vector["document"])
    encoded = canonical(vector["document"])
    assert encoded.hex() == vector["canonical_utf8_hex"]
    assert "sha256:" + hashlib.sha256(encoded).hexdigest() == vector["document_digest"]
    domain = (
        b"FleetForge.agent-release.v1"
        if vector["schema"] == "artifact"
        else b"FleetForge.agent-activation.v1"
    )
    message = domain + b"\0" + encoded
    assert message.hex() == vector["signature_message_hex"]
    key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(vector["public_key"]))
    signature = bytes.fromhex(vector["signature"])
    key.verify(signature, message)
    for wrong_domain in (
        b"FleetForge.release.v1",
        b"FleetForge.agent-activation.v1"
        if vector["schema"] == "artifact"
        else b"FleetForge.agent-release.v1",
    ):
        with pytest.raises(InvalidSignature):
            key.verify(signature, wrong_domain + b"\0" + encoded)
    with pytest.raises(InvalidSignature):
        key.verify(signature, message + b"\n")
    envelope_schema = json.loads((SCHEMAS / "signature.schema.json").read_bytes())
    Draft202012Validator.check_schema(envelope_schema)
    Draft202012Validator(envelope_schema).validate(
        {
            "schema_version": 1,
            "document_digest": vector["document_digest"],
            "signature": vector["signature"],
        }
    )


def test_agent_schema_required_and_closed_objects() -> None:
    """Every required binding must survive neither omission nor extra fields."""
    for vector in VECTORS:
        schema = json.loads((SCHEMAS / f"{vector['schema']}.schema.json").read_bytes())
        validator = Draft202012Validator(schema)
        for field in vector["document"]:
            missing = copy.deepcopy(vector["document"])
            del missing[field]
            assert not validator.is_valid(missing), field
        for path in object_paths(vector["document"]):
            altered = copy.deepcopy(vector["document"])
            node = altered
            for field in path:
                node = node[field]
            node["unexpected"] = True
            assert not validator.is_valid(altered), path


def object_paths(value: dict[str, Any]) -> list[list[str]]:
    paths: list[list[str]] = [[]]
    for field, child in value.items():
        if isinstance(child, dict):
            paths.extend([[field, *path] for path in object_paths(child)])
    return paths


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("kind", "workload-release"),
        ("platform", "osx-arm64"),
        ("version", "01.0.0"),
        ("rust_target", "aarch64-unknown-linux-gnu"),
    ],
)
def test_unsupported_artifact_fields(field: str, value: str) -> None:
    document = copy.deepcopy(VECTORS[0]["document"])
    document[field] = value
    schema = json.loads((SCHEMAS / "artifact.schema.json").read_bytes())
    assert not Draft202012Validator(schema).is_valid(document)
