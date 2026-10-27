"""Shared A/B inputs for portable Python tests."""

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture(params=["a", "b"], ids=["release-a", "release-b"])
def workload(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> ModuleType:
    root = Path(__file__).resolve().parents[2]
    release = root / f"releases/ros-counter-{request.param}-v1"
    spec = importlib.util.spec_from_file_location(
        "fixture_common", release / "app/common.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load common module from {release}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("FLEETFORGE_RELEASE_ID", release.name)
    monkeypatch.setenv(
        "FLEETFORGE_DESCRIPTOR_DIGEST",
        "sha256:" + hashlib.sha256((release / "release.json").read_bytes()).hexdigest(),
    )
    monkeypatch.setenv("FLEETFORGE_PROCESS_INSTANCE_ID", "a" * 32)
    monkeypatch.setenv("ROS_DOMAIN_ID", "42")
    return module
