"""Portable regressions for wire parsing and fixture process boundaries."""

import signal
import subprocess
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, call, patch

import pytest

import check_workloads


def test_decodes_valid_challenge(workload: ModuleType) -> None:
    assert workload.strict_object('{"nonce":"example","sample":0}') == {
        "nonce": "example",
        "sample": 0,
    }


@pytest.mark.parametrize(
    "message",
    [
        '{"sample":0,"sample":1}',
        "[]",
        '{"sample":NaN}',
        '{"sample":Infinity}',
        '{"sample":-Infinity}',
    ],
)
def test_rejects_duplicate_keys_non_objects_and_invalid_constants(
    workload: ModuleType, message: str
) -> None:
    with pytest.raises(ValueError):
        workload.strict_object(message)


def test_size_limit_counts_utf8_bytes(workload: ModuleType) -> None:
    # Each é uses two UTF-8 bytes: below 4096 characters, above 4096 bytes.
    message = '{"value":"' + "é" * 2100 + '"}'
    assert len(message) < 4096
    with pytest.raises(ValueError, match="oversized"):
        workload.strict_object(message)


def test_deep_nesting_is_a_validation_failure(workload: ModuleType) -> None:
    message = '{"value":' + "[" * 1500 + "0" + "]" * 1500 + "}"
    assert len(message.encode()) < 4096
    with pytest.raises(ValueError, match="nested|nesting"):
        workload.strict_object(message)


@pytest.mark.parametrize("message", ['{"value":"\ud800"}', '{"value":"\\ud800"}'])
def test_invalid_unicode_is_a_validation_failure(
    workload: ModuleType, message: str
) -> None:
    with pytest.raises(ValueError, match="Unicode"):
        workload.strict_object(message)


def test_exit_between_poll_and_interrupt_still_reaps_child() -> None:
    child = Mock(spec=subprocess.Popen)
    child.pid = 12345
    child.poll.return_value = None
    with patch("check_workloads.os.killpg", side_effect=ProcessLookupError):
        check_workloads.stop_process_group(child)
    child.wait.assert_called_once_with(timeout=5)


def test_escalation_tolerates_exit_before_kill() -> None:
    child = Mock(spec=subprocess.Popen)
    child.pid = 12345
    child.poll.return_value = None
    child.wait.side_effect = [subprocess.TimeoutExpired("counter", 5), 0]
    with patch(
        "check_workloads.os.killpg", side_effect=[None, ProcessLookupError]
    ) as killpg:
        check_workloads.stop_process_group(child)
    assert killpg.call_args_list == [
        call(child.pid, signal.SIGINT),
        call(child.pid, signal.SIGKILL),
    ]
    assert child.wait.call_count == 2


def test_probe_timeout_has_actionable_retryable_error() -> None:
    expired = subprocess.TimeoutExpired("health", 0.25)
    with (
        patch("check_workloads.subprocess.run", side_effect=expired) as run,
        pytest.raises(
            check_workloads.ProbeTimeoutError, match="health process exceeded 0.25s"
        ) as result,
    ):
        check_workloads.run_probe_process(["health"], Path("/tmp"), {}, 0.25)
    assert result.value.__cause__ is expired
    assert run.call_args.kwargs["timeout"] == 0.25


def test_startup_retries_timeout_with_remaining_budget() -> None:
    release = Mock(spec=check_workloads.Release)
    release.descriptor = {"health": {"startup_timeout_ms": 30000}}
    child = Mock(spec=subprocess.Popen)
    child.poll.return_value = None
    clock = [10.0]
    budgets: list[float] = []

    def probe(environment: dict[str, str], *, timeout: float) -> dict[str, object]:
        budgets.append(timeout)
        clock[0] += 5.0
        if len(budgets) == 1:
            raise RuntimeError("health process exceeded 5s deadline")
        return {"status": "healthy"}

    def sleep(seconds: float) -> None:
        clock[0] += seconds

    release.probe.side_effect = probe
    with (
        patch("check_workloads.time.monotonic", side_effect=lambda: clock[0]),
        patch("check_workloads.time.sleep", side_effect=sleep),
    ):
        check_workloads.Release.ready(release, {}, child)
    assert budgets == pytest.approx([30.0, 24.9])


def test_startup_deadline_preserves_last_probe_failure() -> None:
    release = Mock(spec=check_workloads.Release)
    release.descriptor = {"health": {"startup_timeout_ms": 30000}}
    child = Mock(spec=subprocess.Popen)
    child.poll.return_value = None
    clock = [10.0]
    failure = RuntimeError("health process exceeded 5s deadline")

    def probe(environment: dict[str, str], *, timeout: float) -> dict[str, object]:
        clock[0] += timeout
        raise failure

    release.probe.side_effect = probe
    with (
        patch("check_workloads.time.monotonic", side_effect=lambda: clock[0]),
        patch("check_workloads.time.sleep"),
        pytest.raises(RuntimeError, match="startup health deadline exceeded") as result,
    ):
        check_workloads.Release.ready(release, {}, child)
    assert result.value.__cause__ is failure


@pytest.mark.parametrize(
    "discovery_failure",
    [
        "release_unhealthy: ROS health deadline exceeded",
        check_workloads.ProbeTimeoutError("health process exceeded 5s deadline"),
    ],
)
def test_inactive_requires_observed_state_after_discovery_timeout(
    discovery_failure: str | Exception,
) -> None:
    release = Mock(spec=check_workloads.Release)
    release.descriptor = {"health": {"startup_timeout_ms": 30000}}
    child = Mock(spec=subprocess.Popen)
    child.poll.return_value = None
    clock = [10.0]
    budgets: list[float] = []

    def probe(environment: dict[str, str], healthy: bool, *, timeout: float) -> str:
        assert not healthy
        budgets.append(timeout)
        clock[0] += 5.0
        if len(budgets) == 1:
            if isinstance(discovery_failure, Exception):
                raise discovery_failure
            return discovery_failure
        return "release_unhealthy: ROS lifecycle service is not active"

    def sleep(seconds: float) -> None:
        clock[0] += seconds

    release.probe.side_effect = probe
    with (
        patch("check_workloads.time.monotonic", side_effect=lambda: clock[0]),
        patch("check_workloads.time.sleep", side_effect=sleep),
    ):
        check_workloads.Release.inactive(release, {}, child)
    assert budgets == pytest.approx([30.0, 24.9])


def test_inactive_discovery_timeout_never_counts_as_observed_state() -> None:
    release = Mock(spec=check_workloads.Release)
    release.descriptor = {"health": {"startup_timeout_ms": 30000}}
    child = Mock(spec=subprocess.Popen)
    child.poll.return_value = None
    clock = [10.0]

    def probe(environment: dict[str, str], healthy: bool, *, timeout: float) -> str:
        clock[0] += timeout
        return "release_unhealthy: ROS health deadline exceeded"

    release.probe.side_effect = probe
    with (
        patch("check_workloads.time.monotonic", side_effect=lambda: clock[0]),
        patch("check_workloads.time.sleep"),
        pytest.raises(
            RuntimeError,
            match="inactive lifecycle deadline exceeded:.*ROS health deadline exceeded",
        ),
    ):
        check_workloads.Release.inactive(release, {}, child)


@pytest.mark.parametrize(
    "failure",
    [
        "release_unhealthy: workload identity mismatch",
        RuntimeError("unhealthy probe unexpectedly succeeded: healthy output"),
    ],
)
def test_inactive_does_not_retry_unexpected_failure(failure: str | Exception) -> None:
    release = Mock(spec=check_workloads.Release)
    release.descriptor = {"health": {"startup_timeout_ms": 30000}}
    release.probe.side_effect = [failure]
    child = Mock(spec=subprocess.Popen)
    child.poll.return_value = None
    with (
        patch("check_workloads.time.sleep") as sleep,
        pytest.raises(RuntimeError, match="identity mismatch|unexpectedly succeeded"),
    ):
        check_workloads.Release.inactive(release, {}, child)
    sleep.assert_not_called()


@pytest.mark.parametrize("exit_status", [[0], [None, 0]])
def test_inactive_rejects_dead_process_even_with_inactive_response(
    exit_status: list[int | None],
) -> None:
    release = Mock(spec=check_workloads.Release)
    release.descriptor = {"health": {"startup_timeout_ms": 30000}}
    release.probe.return_value = (
        "release_unhealthy: ROS lifecycle service is not active"
    )
    child = Mock(spec=subprocess.Popen)
    child.poll.side_effect = exit_status
    with pytest.raises(RuntimeError, match="inactive workload.*died"):
        check_workloads.Release.inactive(release, {}, child)
