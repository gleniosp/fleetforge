"""Bounded lifecycle service plus nonce/counter ROS message verification."""

import json
import os
import re
import secrets
import sys
import time
from collections.abc import Callable

import rclpy
from lifecycle_msgs.msg import State
from lifecycle_msgs.srv import GetState
from rclpy.node import Node
from std_msgs.msg import String

from common import STEP, Identity, identity, namespace, strict_object


class Probe(Node):
    """Verify one process using its lifecycle service and two fresh samples."""

    def __init__(self, current: Identity, nonce: str) -> None:
        super().__init__(
            "probe_" + secrets.token_hex(8),
            namespace=namespace(current),
            enable_rosout=False,
            start_parameter_services=False,
        )
        self.current = current
        self.nonce = nonce
        self.samples: dict[int, int] = {}
        self.failure: str | None = None
        self.output = self.create_publisher(String, "challenge", 10)
        self.input = self.create_subscription(String, "reply", self.receive, 10)
        self.state = self.create_client(GetState, "counter/get_state")

    def receive(self, message: String) -> None:
        """Validate replies for this nonce, preserving any protocol failure."""
        try:
            value = strict_object(message.data)
            if value.get("nonce") != self.nonce:
                return
            if set(value) != {*self.current, "nonce", "sample", "counter", "lifecycle"}:
                raise ValueError("unexpected response fields")
            if any(value[key] != expected for key, expected in self.current.items()):
                raise ValueError("workload identity mismatch")
            if value["lifecycle"] != "active":
                raise ValueError("workload lifecycle inactive")
            sample = value["sample"]
            if type(sample) is not int or sample not in (0, 1):
                raise ValueError("invalid sample")
            count = value["counter"]
            if type(count) is not int or not 0 < count < 2**63:
                raise ValueError("invalid counter")
            previous = self.samples.setdefault(sample, count)
            if previous != count:
                raise ValueError("conflicting counter response")
        except (ValueError, TypeError, KeyError) as error:
            self.failure = str(error)

    def until(self, predicate: Callable[[], bool], deadline: float) -> None:
        """Spin until a condition holds, using an absolute monotonic deadline."""
        while not predicate():
            if self.failure:
                raise ValueError(self.failure)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("ROS health deadline exceeded")
            rclpy.spin_once(self, timeout_sec=min(0.05, remaining))
        if self.failure:
            raise ValueError(self.failure)

    def check(self, deadline: float) -> dict[str, object]:
        """Return health evidence after observing active state and counter delta."""
        self.until(
            lambda: (
                self.state.service_is_ready()
                and self.output.get_subscription_count() > 0
                and self.count_publishers("reply") > 0
            ),
            deadline,
        )
        state = self.state.call_async(GetState.Request())
        self.until(state.done, deadline)
        response = state.result()
        if response is None or response.current_state.id != State.PRIMARY_STATE_ACTIVE:
            raise ValueError("ROS lifecycle service is not active")
        for sample in (0, 1):
            request = String(data=json.dumps({"nonce": self.nonce, "sample": sample}))
            # A bounded retry tolerates discovery races. The workload deduplicates samples.
            while sample not in self.samples:
                self.output.publish(request)
                retry_end = min(deadline, time.monotonic() + 0.2)

                def received_or_retry_due(
                    sample: int = sample, retry_end: float = retry_end
                ) -> bool:
                    return sample in self.samples or time.monotonic() >= retry_end

                self.until(received_or_retry_due, deadline)
                if time.monotonic() >= deadline and sample not in self.samples:
                    raise TimeoutError("ROS counter response deadline exceeded")
        observed_step = self.samples[1] - self.samples[0]
        if observed_step != STEP:
            raise ValueError(f"counter delta {observed_step}, expected {STEP}")
        return {
            "schema_version": 1,
            "status": "healthy",
            **self.current,
            "nonce": self.nonce,
            "observed_behavior": f"counter-step-{observed_step}",
        }


def main() -> None:
    """Print one bounded success document, or let the CLI report failure."""
    current = identity()
    nonce = os.environ["FLEETFORGE_HEALTH_NONCE"]
    if not re.fullmatch(r"[0-9a-f]{64}", nonce):
        raise ValueError("invalid health nonce")
    # Leave headroom inside the descriptor's 5000 ms parent process deadline.
    deadline = time.monotonic() + 4.0
    rclpy.init(args=[])
    node: Probe | None = None
    try:
        node = Probe(current, nonce)
        result = node.check(deadline)
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, RuntimeError, TimeoutError) as error:
        print(f"release_unhealthy: {error}", file=sys.stderr)
        sys.exit(1)
