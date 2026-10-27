"""Run the real ROS demonstration through pytest in fresh runtime copies."""

import shutil
import subprocess
from pathlib import Path

import pytest

from check_workloads import verify_workloads


@pytest.mark.ros
def test_real_ros_workloads(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[2]
    pixi = shutil.which("pixi")
    assert pixi is not None, "host-installed Pixi is required"
    for release_id in ("ros-counter-a-v1", "ros-counter-b-v1"):
        release = tmp_path / release_id
        shutil.copytree(source / "releases" / release_id, release)
        subprocess.run(
            [
                pixi,
                "install",
                "--locked",
                "--manifest-path",
                str(release / "pixi.toml"),
            ],
            check=True,
            timeout=600,
        )
    verify_workloads(pixi, tmp_path, source)
