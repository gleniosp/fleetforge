"""Dependency-free regressions for wire parsing and fixture process boundaries.

Run with the release interpreter via run-demo.sh. The broader pytest/tooling
suite belongs to #12; these checks need only the Python standard library.
"""

import importlib.util
import io
import signal
import subprocess
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType
from typing import ClassVar
from unittest.mock import Mock, call, patch

import check_workloads


class WireFormatTests(unittest.TestCase):
    modules: ClassVar[list[ModuleType]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.modules = []
        root = Path(__file__).resolve().parents[2]
        for label in ("a", "b"):
            path = root / f"releases/ros-counter-{label}-v1/app/common.py"
            spec = importlib.util.spec_from_file_location(f"common_{label}", path)
            if spec is None or spec.loader is None:
                raise ImportError(f"cannot load {path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            cls.modules.append(module)

    def test_decodes_valid_challenge(self) -> None:
        for module in self.modules:
            with self.subTest(release=module.RELEASE_ID):
                self.assertEqual(
                    module.strict_object('{"nonce":"example","sample":0}'),
                    {"nonce": "example", "sample": 0},
                )

    def test_rejects_duplicate_keys_non_objects_and_invalid_constants(self) -> None:
        messages = (
            '{"sample":0,"sample":1}',
            "[]",
            '{"sample":NaN}',
            '{"sample":Infinity}',
            '{"sample":-Infinity}',
        )
        for module in self.modules:
            for message in messages:
                with self.subTest(release=module.RELEASE_ID, message=message):
                    with self.assertRaises(ValueError):
                        module.strict_object(message)

    def test_size_limit_counts_utf8_bytes(self) -> None:
        message = '{"value":"' + "é" * 2100 + '"}'
        self.assertLess(len(message), 4096)
        for module in self.modules:
            with self.subTest(release=module.RELEASE_ID):
                with self.assertRaisesRegex(ValueError, "oversized"):
                    module.strict_object(message)

    def test_deep_nesting_is_a_validation_failure(self) -> None:
        message = '{"value":' + "[" * 1500 + "0" + "]" * 1500 + "}"
        self.assertLess(len(message.encode()), 4096)
        for module in self.modules:
            with self.subTest(release=module.RELEASE_ID):
                with self.assertRaisesRegex(ValueError, "nested|nesting"):
                    module.strict_object(message)

    def test_invalid_unicode_is_a_validation_failure(self) -> None:
        for module in self.modules:
            for message in ('{"value":"\ud800"}', '{"value":"\\ud800"}'):
                with self.subTest(release=module.RELEASE_ID, message=repr(message)):
                    with self.assertRaisesRegex(ValueError, "Unicode"):
                        module.strict_object(message)


class ProcessBoundaryTests(unittest.TestCase):
    def test_exit_between_poll_and_interrupt_still_reaps_child(self) -> None:
        child = Mock(spec=subprocess.Popen)
        child.pid = 12345
        child.poll.return_value = None
        with patch.object(check_workloads.os, "killpg", side_effect=ProcessLookupError):
            check_workloads.stop_process_group(child)
        child.wait.assert_called_once_with(timeout=5)

    def test_escalation_tolerates_exit_before_kill(self) -> None:
        child = Mock(spec=subprocess.Popen)
        child.pid = 12345
        child.poll.return_value = None
        child.wait.side_effect = [subprocess.TimeoutExpired("counter", 5), 0]
        with patch.object(
            check_workloads.os, "killpg", side_effect=[None, ProcessLookupError]
        ) as killpg:
            check_workloads.stop_process_group(child)
        self.assertEqual(
            killpg.call_args_list,
            [call(child.pid, signal.SIGINT), call(child.pid, signal.SIGKILL)],
        )
        self.assertEqual(child.wait.call_count, 2)

    def test_probe_timeout_has_actionable_retryable_error(self) -> None:
        expired = subprocess.TimeoutExpired("health", 0.25)
        with patch.object(
            check_workloads.subprocess, "run", side_effect=expired
        ) as run:
            with self.assertRaisesRegex(
                RuntimeError, "health process exceeded 0.25s"
            ) as result:
                check_workloads.run_probe_process(["health"], Path("/tmp"), {}, 0.25)
        self.assertIs(result.exception.__cause__, expired)
        self.assertEqual(run.call_args.kwargs["timeout"], 0.25)

    def test_startup_retries_timeout_with_remaining_budget(self) -> None:
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
            patch.object(
                check_workloads.time, "monotonic", side_effect=lambda: clock[0]
            ),
            patch.object(check_workloads.time, "sleep", side_effect=sleep),
            redirect_stdout(io.StringIO()),
        ):
            check_workloads.Release.ready(release, {}, child)
        self.assertEqual(len(budgets), 2)
        self.assertAlmostEqual(budgets[0], 30.0)
        self.assertAlmostEqual(budgets[1], 24.9)

    def test_startup_deadline_preserves_last_probe_failure(self) -> None:
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
            patch.object(
                check_workloads.time, "monotonic", side_effect=lambda: clock[0]
            ),
            patch.object(check_workloads.time, "sleep"),
        ):
            with self.assertRaisesRegex(
                RuntimeError, "startup health deadline exceeded"
            ) as result:
                check_workloads.Release.ready(release, {}, child)
        self.assertIs(result.exception.__cause__, failure)


if __name__ == "__main__":
    unittest.main(verbosity=2)
