"""Local demonstration control used to prove inactive nodes fail health."""

import argparse
import math
import os
import sys
import time

import rclpy
from lifecycle_msgs.msg import Transition
from lifecycle_msgs.srv import ChangeState
from rclpy.node import Node


def main() -> None:
    """Request a real transition within one discovery/response deadline."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transition", choices=("activate", "deactivate"))
    parser.add_argument(
        "--timeout",
        type=float,
        default=4.0,
        help="Combined discovery/transition deadline in seconds (default: %(default)s)",
    )
    arguments = parser.parse_args()
    if not math.isfinite(arguments.timeout) or arguments.timeout <= 0:
        parser.error("--timeout must be a finite positive number of seconds")
    transition_id = {
        "activate": Transition.TRANSITION_ACTIVATE,
        "deactivate": Transition.TRANSITION_DEACTIVATE,
    }[arguments.transition]
    instance = os.environ["FLEETFORGE_PROCESS_INSTANCE_ID"]
    rclpy.init(args=[])
    node: Node | None = None
    try:
        node = Node(
            "fixture_control", enable_rosout=False, start_parameter_services=False
        )
        client = node.create_client(
            ChangeState, f"/fleetforge/i_{instance}/counter/change_state"
        )
        deadline = time.monotonic() + arguments.timeout
        if not client.wait_for_service(
            timeout_sec=max(0.0, deadline - time.monotonic())
        ):
            raise RuntimeError("lifecycle service unavailable")
        request = ChangeState.Request()
        request.transition.id = transition_id
        result = client.call_async(request)
        rclpy.spin_until_future_complete(
            node, result, timeout_sec=max(0.0, deadline - time.monotonic())
        )
        response = result.result() if result.done() else None
        if response is None or not response.success:
            raise RuntimeError("lifecycle transition failed")
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    try:
        main()
    except (KeyError, RuntimeError) as error:
        print(f"lifecycle control failed: {error}", file=sys.stderr)
        sys.exit(1)
