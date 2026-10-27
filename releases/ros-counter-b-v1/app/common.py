"""Local fixture identity and wire format; release validation belongs to #13/#86."""

import hashlib
import json
import os
import re
from pathlib import Path
from typing import NoReturn, TypedDict

RELEASE_ID = "ros-counter-b-v1"
STEP = 2


class Identity(TypedDict):
    """Release and process identity carried by every successful response."""

    release_id: str
    descriptor_digest: str
    process_instance_id: str


def identity() -> Identity:
    """Validate this process's supplied identity against its local release."""
    release_id = os.environ["FLEETFORGE_RELEASE_ID"]
    digest = os.environ["FLEETFORGE_DESCRIPTOR_DIGEST"]
    instance = os.environ["FLEETFORGE_PROCESS_INSTANCE_ID"]
    descriptor = Path(__file__).resolve().parents[1] / "release.json"
    actual_digest = "sha256:" + hashlib.sha256(descriptor.read_bytes()).hexdigest()
    if release_id != RELEASE_ID or digest != actual_digest:
        raise ValueError("release identity does not match these workload inputs")
    if not re.fullmatch(r"[0-9a-f]{32}", instance):
        raise ValueError("invalid process instance")
    domain = os.environ["ROS_DOMAIN_ID"]
    if not domain.isdecimal() or not 0 <= int(domain) <= 101:
        raise ValueError("fixture requires ROS_DOMAIN_ID in 0..101")
    return {
        "release_id": release_id,
        "descriptor_digest": digest,
        "process_instance_id": instance,
    }


def namespace(value: Identity) -> str:
    """Return the ROS namespace reserved for this running attempt."""
    return "/fleetforge/i_" + value["process_instance_id"]


def strict_object(text: str) -> dict[str, object]:
    """Decode a bounded flat JSON object; invalid wire input raises ValueError."""

    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON field")
            # ASCII JSON escapes can still decode into unpaired surrogates.
            key.encode("utf-8")
            if isinstance(value, str):
                value.encode("utf-8")
            result[key] = value
        return result

    def reject_constant(value: str) -> NoReturn:
        raise ValueError(f"invalid JSON constant: {value}")

    try:
        if len(text.encode("utf-8")) > 4096:
            raise ValueError("oversized ROS message")
        value = json.loads(
            text, object_pairs_hook=unique, parse_constant=reject_constant
        )
    except (UnicodeError, RecursionError) as error:
        # Even a sub-4-KiB message can exceed the decoder's nesting limit.
        raise ValueError("invalid Unicode or excessive JSON nesting") from error
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    if any(isinstance(item, (dict, list)) for item in value.values()):
        raise ValueError("nested JSON values are not supported")
    return value
