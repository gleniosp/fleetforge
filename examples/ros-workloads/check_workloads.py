"""Real-process A/B compatibility and health evidence, using disposable copies.

This deliberately unsigned fixture is neither a release-check implementation
nor a production supervisor. #13, #86 and the deployment slices own those.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import signal
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Literal, overload


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def snapshot(root: Path) -> dict[str, str]:
    """Fingerprint source files so a run can detect accidental mutation."""
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def stop_process_group(child: subprocess.Popen[bytes]) -> None:
    """Interrupt, escalate if necessary, and reap a fixture's process group."""
    if child.poll() is not None:
        return
    try:
        os.killpg(child.pid, signal.SIGINT)
    except ProcessLookupError:
        # The child may exit between poll() and killpg(); still reap it below.
        pass
    try:
        child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        child.wait(timeout=5)


class ProbeTimeoutError(RuntimeError):
    """A probe process exhausted its allotted verification time."""


def run_probe_process(
    command: list[str], root: Path, environment: dict[str, str], timeout: float
) -> subprocess.CompletedProcess[str]:
    """Run a health process; expiry is a retryable startup verification failure."""
    try:
        return subprocess.run(
            command,
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise ProbeTimeoutError(
            f"health process exceeded {timeout:g}s deadline"
        ) from error


class Release:
    """Run a trusted, developer-owned descriptor in its independent environment."""

    def __init__(self, root: Path, pixi: str, logs: Path) -> None:
        self.root = root
        self.logs = logs
        self.descriptor = json.loads((root / "release.json").read_bytes())
        self.digest = (
            "sha256:" + hashlib.sha256((root / "release.json").read_bytes()).hexdigest()
        )
        for item in self.descriptor["files"]:
            payload = (root / item["path"]).read_bytes()
            require(len(payload) == item["size"], "fixture size mismatch")
            require(
                hashlib.sha256(payload).hexdigest() == item["sha256"],
                "fixture hash mismatch: " + item["path"],
            )
        # Activation code is trusted here only because these are developer-owned fixtures.
        clean = {"PATH": os.defpath, "HOME": str(logs), "LANG": "C.UTF-8"}
        result = subprocess.run(
            [
                pixi,
                "shell-hook",
                "--locked",
                "--manifest-path",
                str(root / "pixi.toml"),
                "--json",
            ],
            env=clean,
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.activation = json.loads(result.stdout)["environment_variables"]
        self.environment = {**clean, **self.activation}
        self.environment.update(
            {
                "PYTHONNOUSERSITE": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
                "ROS_LOG_DIR": str(logs),
                "RCUTILS_LOGGING_USE_STDOUT": "0",
                "ROS_AUTOMATIC_DISCOVERY_RANGE": "LOCALHOST",
                "RMW_IMPLEMENTATION": "rmw_fastrtps_cpp",
            }
        )
        self.python = root / ".pixi/envs/default/bin/python"
        require(self.python.exists(), "missing independent Python environment")
        prefix = self.python.parents[1]
        require(
            Path(self.environment["CONDA_PREFIX"]) == prefix,
            "activation selected the wrong runtime prefix",
        )
        packages = [
            json.loads(path.read_bytes())
            for path in sorted((prefix / "conda-meta").glob("*.json"))
        ]
        selected = {
            item["name"]: item["version"]
            for item in packages
            if item["name"]
            in {
                "python",
                "ros2-rclpy",
                "ros2-std-msgs",
                "ros2-lifecycle-msgs",
                "ros2-rmw-fastrtps-cpp",
            }
        }
        print(
            json.dumps(
                {"runtime": root.name, "packages": len(packages), "versions": selected}
            ),
            flush=True,
        )

    def context(self, domain: int, instance: str | None = None) -> dict[str, str]:
        """Build the isolated environment for one running attempt."""
        return {
            **self.environment,
            "ROS_DOMAIN_ID": str(domain),
            "FLEETFORGE_RELEASE_ID": self.descriptor["release_id"],
            "FLEETFORGE_DESCRIPTOR_DIGEST": self.digest,
            "FLEETFORGE_PROCESS_INSTANCE_ID": instance or secrets.token_hex(16),
        }

    def command(self, name: Literal["main", "health"]) -> list[str]:
        command = self.descriptor["entrypoint" if name == "main" else "health"]
        return [
            str(self.root / ".pixi/envs/default" / command["argv"][0]),
            *command["argv"][1:],
        ]

    @contextmanager
    def running(
        self, env: dict[str, str], faulty_step: bool = False
    ) -> Iterator[subprocess.Popen[bytes]]:
        """Keep the child and its log alive for the duration of the context."""
        log_path = self.logs / (env["FLEETFORGE_PROCESS_INSTANCE_ID"] + ".log")
        with log_path.open("ab") as log:
            command = self.command("main")
            if faulty_step:
                command = [
                    str(self.python),
                    "-c",
                    "import sys; sys.path.insert(0, 'app'); "
                    "import main; main.STEP = 2; main.main()",
                ]
            child = subprocess.Popen(
                command,
                cwd=self.root,
                env=env,
                stdout=log,
                stderr=log,
                start_new_session=True,
            )
            try:
                yield child
            finally:
                stop_process_group(child)
                if child.returncode != 0:
                    print(
                        log_path.read_text(encoding="utf-8", errors="replace")[-8192:],
                        file=sys.stderr,
                    )

    @overload
    def probe(
        self,
        env: dict[str, str],
        healthy: Literal[True] = True,
        *,
        timeout: float | None = None,
    ) -> dict[str, object]: ...

    @overload
    def probe(
        self,
        env: dict[str, str],
        healthy: Literal[False],
        *,
        timeout: float | None = None,
    ) -> str: ...

    def probe(
        self, env: dict[str, str], healthy: bool = True, *, timeout: float | None = None
    ) -> dict[str, object] | str:
        """Check a fresh nonce and exact identity, or require an unhealthy result."""
        nonce = secrets.token_hex(32)
        current = {**env, "FLEETFORGE_HEALTH_NONCE": nonce}
        probe_timeout = self.descriptor["health"]["probe_timeout_ms"] / 1000
        if timeout is not None:
            probe_timeout = min(probe_timeout, timeout)
        result = run_probe_process(
            self.command("health"), self.root, current, probe_timeout
        )
        if not healthy:
            require(
                result.returncode != 0 and not result.stdout.strip(),
                "unhealthy probe unexpectedly succeeded: " + result.stdout,
            )
            require(
                "release_unhealthy:" in result.stderr,
                "unhealthy probe failed without an actionable error: " + result.stderr,
            )
            return result.stderr.strip()
        require(result.returncode == 0, "health failed: " + result.stderr)
        require(len(result.stdout.encode()) <= 4096, "oversized health output")
        value: dict[str, object] = json.loads(result.stdout)
        expected = {
            "schema_version": 1,
            "status": "healthy",
            "release_id": env["FLEETFORGE_RELEASE_ID"],
            "descriptor_digest": env["FLEETFORGE_DESCRIPTOR_DIGEST"],
            "process_instance_id": env["FLEETFORGE_PROCESS_INSTANCE_ID"],
            "nonce": nonce,
            "observed_behavior": self.descriptor["health"]["expected_behavior"],
        }
        require(value == expected, "probe output disagrees with expected attempt")
        return value

    def ready(self, env: dict[str, str], child: subprocess.Popen[bytes]) -> None:
        """Retry bounded health checks within the descriptor's startup budget."""
        deadline = (
            time.monotonic() + self.descriptor["health"]["startup_timeout_ms"] / 1000
        )
        last_error: RuntimeError | None = None
        while time.monotonic() < deadline:
            require(child.poll() is None, "workload exited before verification")
            try:
                result = self.probe(env, timeout=deadline - time.monotonic())
                require(child.poll() is None, "workload exited during verification")
                print(json.dumps(result), flush=True)
                return
            except RuntimeError as error:
                last_error = error
                time.sleep(min(0.1, max(0.0, deadline - time.monotonic())))
        raise RuntimeError(
            f"startup health deadline exceeded: {last_error}"
        ) from last_error

    def inactive(self, env: dict[str, str], child: subprocess.Popen[bytes]) -> None:
        """Require observed inactive state, allowing bounded fresh-probe discovery."""
        deadline = (
            time.monotonic() + self.descriptor["health"]["startup_timeout_ms"] / 1000
        )
        last_reason = "no probe completed"
        while time.monotonic() < deadline:
            require(child.poll() is None, "inactive workload unexpectedly died")
            try:
                reason = self.probe(env, False, timeout=deadline - time.monotonic())
            except ProbeTimeoutError as error:
                last_reason = str(error)
            else:
                require(
                    child.poll() is None, "inactive workload died during verification"
                )
                if reason == "release_unhealthy: ROS lifecycle service is not active":
                    return
                # A new ROS participant can exhaust discovery before querying state.
                # Other failures must remain failures rather than count as inactivity.
                require(
                    reason == "release_unhealthy: ROS health deadline exceeded",
                    "unexpected inactive probe failure: " + reason,
                )
                last_reason = reason
            time.sleep(min(0.1, max(0.0, deadline - time.monotonic())))
        raise RuntimeError("inactive lifecycle deadline exceeded: " + last_reason)


def verify_workloads(pixi: str, fixture: Path, source: Path) -> None:
    """Exercise independent runtimes, positive health and deliberate failures."""
    before = snapshot(source / "releases")
    logs = fixture / "logs"
    logs.mkdir()
    a = Release(fixture / "ros-counter-a-v1", pixi, logs)
    b = Release(fixture / "ros-counter-b-v1", pixi, logs)
    require(
        a.python.resolve() != b.python.resolve(), "A/B share an installed environment"
    )
    # Domains are local to this disposable fixture/container, never a signed release field.
    domain = 30 + secrets.randbelow(50)
    a_env = a.context(domain)
    b_env = b.context(domain + 1)
    # Exercise the real entrypoints, including failure before ROS initialization.
    invalid_invocations: tuple[tuple[Literal["main", "health"], str, str, str], ...] = (
        (
            "main",
            "FLEETFORGE_PROCESS_INSTANCE_ID",
            "invalid",
            "invalid process instance",
        ),
        ("health", "FLEETFORGE_HEALTH_NONCE", "invalid", "invalid health nonce"),
        (
            "health",
            "FLEETFORGE_DESCRIPTOR_DIGEST",
            "sha256:" + "0" * 64,
            "release identity",
        ),
    )
    for release, environment in ((a, a_env), (b, b_env)):
        for name, variable, value, reason in invalid_invocations:
            invalid = subprocess.run(
                release.command(name),
                cwd=release.root,
                env={**environment, variable: value},
                capture_output=True,
                text=True,
                timeout=5,
            )
            require(
                invalid.returncode == 1
                and not invalid.stdout.strip()
                and reason in invalid.stderr,
                "invalid invocation did not fail clearly: "
                + invalid.stdout
                + invalid.stderr,
            )
    print(
        "PASS: invalid process identity, health nonce and descriptor digest rejected",
        flush=True,
    )
    with a.running(a_env) as a_child, b.running(b_env) as b_child:
        a.ready(a_env, a_child)
        b.ready(b_env, b_child)
        # Keep the old A process alive: its endpoint cannot answer a new attempt.
        a.probe(
            {**a_env, "FLEETFORGE_PROCESS_INSTANCE_ID": secrets.token_hex(16)}, False
        )
        print("PASS: unrelated endpoint cannot satisfy health", flush=True)
        # Deliberately route A's probe to B's domain/endpoint: reject its identity.
        reason = a.probe(
            {
                **a_env,
                "FLEETFORGE_PROCESS_INSTANCE_ID": b_env[
                    "FLEETFORGE_PROCESS_INSTANCE_ID"
                ],
                "ROS_DOMAIN_ID": b_env["ROS_DOMAIN_ID"],
            },
            False,
        )
        require(
            "workload identity mismatch" in reason,
            "neighbor test did not observe the wrong workload's actual reply",
        )
        print(
            "PASS: neighbor identity rejected when deliberately routed to its endpoint",
            flush=True,
        )
        # Same endpoint name, wrong ROS domain: discovery must not cross the domain boundary.
        a.probe({**a_env, "ROS_DOMAIN_ID": str(domain + 1)}, False)
        print("PASS: ROS domain isolation", flush=True)
        control = source / "examples/ros-workloads/lifecycle.py"
        unavailable = subprocess.run(
            [str(a.python), str(control), "deactivate", "--timeout", "0.2"],
            env={**a_env, "FLEETFORGE_PROCESS_INSTANCE_ID": secrets.token_hex(16)},
            capture_output=True,
            text=True,
            timeout=5,
        )
        require(
            unavailable.returncode == 1
            and not unavailable.stdout.strip()
            and "lifecycle service unavailable" in unavailable.stderr,
            "unavailable lifecycle service did not fail within its deadline",
        )
        print(
            "PASS: lifecycle control has a bounded unavailable-service failure",
            flush=True,
        )
        transition_timeout = a.descriptor["health"]["startup_timeout_ms"] / 1000
        subprocess.run(
            [
                str(a.python),
                str(control),
                "deactivate",
                "--timeout",
                str(transition_timeout),
            ],
            env=a_env,
            check=True,
            timeout=transition_timeout + 5,
        )
        a.inactive(a_env, a_child)
        print("PASS: live inactive lifecycle fails health", flush=True)
        subprocess.run(
            [
                str(a.python),
                str(control),
                "activate",
                "--timeout",
                str(transition_timeout),
            ],
            env=a_env,
            check=True,
            timeout=transition_timeout + 5,
        )
        a.ready(a_env, a_child)
        # A remains live while B is independently prepared/run, and is still usable.
        b.probe(b_env)
    a.probe(a_env, False)
    print("PASS: stopped workload cannot satisfy health", flush=True)
    # A new attempt cannot reuse the old process endpoint/instance identity.
    next_env = a.context(domain + 2)
    with a.running(next_env) as child:
        a.ready(next_env, child)
        a.probe(a_env, False)
        print("PASS: stale attempt cannot satisfy health after restart", flush=True)
    # Change the actual counter algorithm in a child only, keeping A's probe/identity.
    # The probe must observe the wrong delta rather than trust release metadata.
    faulty_env = a.context(domain + 3)
    with a.running(faulty_env, faulty_step=True) as child:
        deadline = time.monotonic() + 30
        while True:
            require(child.poll() is None, "fault fixture exited")
            reason = a.probe(faulty_env, False)
            if "counter delta 2, expected 1" in reason:
                break
            require(
                time.monotonic() < deadline, "did not observe wrong counter behavior"
            )
        print(
            "PASS: wrong counter behavior fails despite matching release identity",
            flush=True,
        )
    require(
        before == snapshot(source / "releases"), "source release files were modified"
    )
    require(
        not list((source / "releases").rglob(".pixi")),
        "generated output in source inputs",
    )
    print(
        "PASS: independent A/B environments, real ROS behavior, fresh nonce/identity, "
        "lifecycle/domain/endpoint isolation, retained unchanged release inputs",
        flush=True,
    )


def main() -> None:
    """Run the same verification as pytest from the standalone demo."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pixi", help="absolute path to the Pixi executable")
    parser.add_argument(
        "fixture", type=Path, help="disposable installed release copies"
    )
    parser.add_argument(
        "source", type=Path, help="source repository to check for mutation"
    )
    arguments = parser.parse_args()
    verify_workloads(
        arguments.pixi, arguments.fixture.resolve(), arguments.source.resolve()
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"workload checks failed: {error}", file=sys.stderr)
        sys.exit(1)
