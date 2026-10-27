"""Check both immutable releases' identity boundary without importing ROS."""

from types import ModuleType

import pytest


def test_identity_binds_local_release_and_attempt(workload: ModuleType) -> None:
    current = workload.identity()
    assert current["release_id"] == workload.RELEASE_ID
    assert current["process_instance_id"] == "a" * 32
    assert workload.namespace(current) == "/fleetforge/i_" + "a" * 32


@pytest.mark.parametrize(
    ("variable", "value", "reason"),
    [
        ("FLEETFORGE_RELEASE_ID", "another-release", "release identity"),
        ("FLEETFORGE_DESCRIPTOR_DIGEST", "sha256:" + "0" * 64, "release identity"),
        ("FLEETFORGE_PROCESS_INSTANCE_ID", "a" * 31, "invalid process instance"),
        ("FLEETFORGE_PROCESS_INSTANCE_ID", "A" * 32, "invalid process instance"),
        ("FLEETFORGE_PROCESS_INSTANCE_ID", "../neighbor", "invalid process instance"),
        ("ROS_DOMAIN_ID", "-1", "ROS_DOMAIN_ID"),
        ("ROS_DOMAIN_ID", "102", "ROS_DOMAIN_ID"),
        ("ROS_DOMAIN_ID", "invalid", "ROS_DOMAIN_ID"),
    ],
)
def test_identity_rejects_invalid_context(
    workload: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    variable: str,
    value: str,
    reason: str,
) -> None:
    monkeypatch.setenv(variable, value)
    with pytest.raises(ValueError, match=reason):
        workload.identity()


@pytest.mark.parametrize(
    "variable",
    [
        "FLEETFORGE_RELEASE_ID",
        "FLEETFORGE_DESCRIPTOR_DIGEST",
        "FLEETFORGE_PROCESS_INSTANCE_ID",
        "ROS_DOMAIN_ID",
    ],
)
def test_identity_requires_explicit_context(
    workload: ModuleType, monkeypatch: pytest.MonkeyPatch, variable: str
) -> None:
    monkeypatch.delenv(variable)
    with pytest.raises(KeyError, match=variable):
        workload.identity()
