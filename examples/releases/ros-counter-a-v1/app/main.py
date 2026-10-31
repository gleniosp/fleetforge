"""Headless lifecycle counter: A increments by one; B increments by two."""

from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.lifecycle import (
    LifecycleNode,
    LifecyclePublisher,
    LifecycleState,
    TransitionCallbackReturn,
)
from std_msgs.msg import String

from common import STEP, Identity, identity, namespace, strict_object


class Counter(LifecycleNode):
    """Serve counter samples only while the managed publisher is active."""

    def __init__(self, current: Identity) -> None:
        super().__init__(
            "counter",
            namespace=namespace(current),
            enable_rosout=False,
            start_parameter_services=False,
        )
        self.current = current
        self.count = 0
        self.responses: OrderedDict[str, dict[int, int]] = OrderedDict()
        self.output: LifecyclePublisher | None = None

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self.output = self.create_lifecycle_publisher(String, "reply", 10)
        self.input = self.create_subscription(String, "challenge", self.challenge, 10)
        return TransitionCallbackReturn.SUCCESS

    def challenge(self, message: String) -> None:
        """Reply to each nonce/sample once; retries return the cached count."""
        output = self.output
        if output is None or not output.is_activated:
            return
        try:
            request = strict_object(message.data)
            if set(request) != {"nonce", "sample"}:
                return
            nonce, sample = request["nonce"], request["sample"]
            if not isinstance(nonce, str) or not re.fullmatch(r"[0-9a-f]{64}", nonce):
                return
            if type(sample) is not int or sample not in (0, 1):
                return
            if nonce not in self.responses:
                if sample != 0:
                    return
                if len(self.responses) == 64:
                    self.responses.popitem(last=False)
                self.responses[nonce] = {}
            samples = self.responses[nonce]
            if sample not in samples:
                if sample == 1 and 0 not in samples:
                    return
                if self.count > (2**63 - 1) - STEP:
                    return
                self.count += STEP
                samples[sample] = self.count
            response = {
                **self.current,
                "nonce": nonce,
                "sample": sample,
                "counter": samples[sample],
                "lifecycle": "active",
            }
            output.publish(String(data=json.dumps(response, separators=(",", ":"))))
        except ValueError, TypeError, KeyError:
            # Malformed traffic cannot make this process healthy or stop its executor.
            return


def main() -> None:
    """Configure and activate the node, then serve until shutdown."""
    current = identity()
    rclpy.init(args=[])
    node: Counter | None = None
    try:
        node = Counter(current)
        if node.trigger_configure() != TransitionCallbackReturn.SUCCESS:
            raise RuntimeError("counter configuration failed")
        if node.trigger_activate() != TransitionCallbackReturn.SUCCESS:
            raise RuntimeError("counter activation failed")
        print(json.dumps({"event": "active", **current, "step": STEP}), flush=True)
        rclpy.spin(node)
    except KeyboardInterrupt, ExternalShutdownException:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, RuntimeError) as error:
        print(f"workload failed: {error}", file=sys.stderr)
        sys.exit(1)
