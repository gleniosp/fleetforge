"""Encoding boundaries shared by signed workload and agent metadata."""

from typing import Any

import pytest

from tools.json_encoding import CanonicalJSONError, canonical
from tools.releases.catalog import ReleaseError, parse


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"b": [True, None], "a": 1}, b'{"a":1,"b":[true,null]}'),
        ({"\ue000": 1, "\U00010000": 2}, '{"\U00010000":2,"\ue000":1}'.encode()),
        (
            [9007199254740991, -9007199254740991],
            b"[9007199254740991,-9007199254740991]",
        ),
    ],
)
def test_canonical_bytes(value: Any, expected: bytes) -> None:
    assert canonical(value) == expected


@pytest.mark.parametrize(
    "value", [1.5, float("nan"), 9007199254740992, -9007199254740992]
)
def test_reject_noninteroperable_numbers(value: int | float) -> None:
    with pytest.raises(CanonicalJSONError):
        canonical({"nested": [value]})


def test_reject_invalid_unicode() -> None:
    with pytest.raises(UnicodeError):
        canonical({"nested": ["\ud800"]})


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (b"1.5", "non-integer number"),
        (b"9007199254740992", "integer outside interoperable JSON range"),
    ],
)
def test_workload_parser_preserves_classified_errors(data: bytes, message: str) -> None:
    with pytest.raises(ReleaseError, match=message) as error:
        parse(data)
    assert error.value.code == "release_invalid"
