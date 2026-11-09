"""Canonical JSON encoding shared by FleetForge release formats."""

import json
from typing import Any

# Largest integer for which consecutive values remain exact in IEEE-754 binary64.
MAX_SAFE_JSON_INTEGER = 2**53 - 1


class CanonicalJSONError(ValueError):
    """A number cannot be represented in the integer-only contract domain."""


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
    if isinstance(value, float):
        raise CanonicalJSONError("non-integer number")
    if type(value) is int:
        if abs(value) > MAX_SAFE_JSON_INTEGER:
            raise CanonicalJSONError("integer outside interoperable JSON range")
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
