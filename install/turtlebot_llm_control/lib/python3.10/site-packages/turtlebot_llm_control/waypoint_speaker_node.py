import json
import math
import re
import shutil
import sqlite3
import subprocess
import threading
from typing import List, Optional, Tuple

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.node import Node
from std_msgs.msg import String

# Failsafe: if the nearest DB waypoint is this many metres closer than the
# published index, override the published index with the nearest one.
_FAILSAFE_THRESHOLD_M = 0.5


def _run_tts(text: str) -> None:
    for cmd in (["spd-say", "-w", text], ["espeak", text], ["say", text]):
        if shutil.which(cmd[0]):
            subprocess.run(cmd, check=False)
            return
    print(f"[waypoint_speaker] No TTS available. Would say: {text}")


class WaypointSpeakerNode(Node):
    def __init__(self):
        super().__init__("waypoint_speaker_node")
        self.declare_parameter("db_path", "tours.db")
        self._db_path = self.get_parameter("db_path").get_parameter_value().string_value

        self._current_pose: Optional[Tuple[float, float]] = None
        self._speaking_lock = threading.Lock()

        self._talk_sub = self.create_subscription(
            String, "/talk_command", self._on_talk_command, 10
        )
        self._amcl_sub = self.create_subscription(
            PoseWithCovarianceStamped, "/amcl_pose", self._on_amcl_pose, 10
        )

        self._done_talking_pub = self.create_publisher(String, "/done_talking", 10)
        self._done_speaking_pub = self.create_publisher(String, "/done_speaking", 10)
        self._emotion_pub = self.create_publisher(String, "/robot/emotion", 10)

        self.get_logger().info(f"Waypoint speaker ready. db_path={self._db_path}")

    # ── pose tracking ──────────────────────────────────────────────────────

    def _on_amcl_pose(self, msg: PoseWithCovarianceStamped) -> None:
        pos = msg.pose.pose.position
        self._current_pose = (pos.x, pos.y)

    # ── main handler ───────────────────────────────────────────────────────

    def _on_talk_command(self, msg: String) -> None:
        numbers = re.findall(r"\d+", msg.data)
        if not numbers:
            self.get_logger().warning(f"No integer in talk_command: {msg.data!r}")
            self._signal_done()
            return

        published_index = int(numbers[-1])
        waypoints = self._fetch_all_waypoints()
        resolved_index, used_failsafe = self._resolve_index(published_index, waypoints)

        if used_failsafe:
            self.get_logger().info(
                f"Failsafe: published index {published_index} overridden "
                f"by nearest waypoint at index {resolved_index}"
            )
            self._publish_emotion(
                "curious",
                f"corrected to nearest waypoint {resolved_index}",
                0.60,
            )
        else:
            self._publish_emotion(
                "informative",
                f"explaining waypoint {resolved_index}",
                0.75,
            )

        if resolved_index < len(waypoints):
            description = waypoints[resolved_index][2]
        else:
            description = ""

        if description:
            text = description
        else:
            text = f"Arrived at waypoint {resolved_index}."
            self.get_logger().info(
                f"No description for index {resolved_index}, using fallback."
            )
            self._publish_emotion(
                "puzzled",
                f"no description for waypoint {resolved_index}",
                0.45,
            )

        self.get_logger().info(
            f"Speaking: '{text[:80]}{'...' if len(text) > 80 else ''}'"
        )

        def _speak_then_signal():
            with self._speaking_lock:
                _run_tts(text)
            self._publish_emotion("satisfied", "finished explanation", 0.55)
            self._signal_done()

        threading.Thread(target=_speak_then_signal, daemon=True).start()

    # ── DB helpers ─────────────────────────────────────────────────────────

    def _fetch_all_waypoints(self) -> List[Tuple[float, float, str]]:
        """Return (px, py, description) tuples in insertion order."""
        try:
            con = sqlite3.connect(self._db_path)
            rows = con.execute("SELECT px, py, description FROM tours").fetchall()
            con.close()
            return [(float(r[0]), float(r[1]), str(r[2] or "").strip()) for r in rows]
        except sqlite3.OperationalError as exc:
            self.get_logger().warning(f"DB query failed: {exc}")
            return []

    # ── failsafe index resolution ──────────────────────────────────────────

    def _resolve_index(
        self,
        published_index: int,
        waypoints: List[Tuple[float, float, str]],
    ) -> Tuple[int, bool]:
        """Return (resolved_index, used_failsafe).

        Overrides published_index with the nearest waypoint's index when the
        robot is more than _FAILSAFE_THRESHOLD_M closer to a different waypoint.
        """
        if not waypoints or self._current_pose is None:
            return published_index, False

        rx, ry = self._current_pose

        def dist(i: int) -> float:
            return math.hypot(rx - waypoints[i][0], ry - waypoints[i][1])

        nearest_idx = min(range(len(waypoints)), key=dist)
        nearest_dist = dist(nearest_idx)

        if published_index < len(waypoints):
            published_dist = dist(published_index)
        else:
            published_dist = float("inf")

        if nearest_idx != published_index and (published_dist - nearest_dist) > _FAILSAFE_THRESHOLD_M:
            return nearest_idx, True

        return published_index, False

    # ── signalling ─────────────────────────────────────────────────────────

    def _signal_done(self) -> None:
        done_msg = String(data="done_speaking")
        self._done_talking_pub.publish(done_msg)
        self._done_speaking_pub.publish(done_msg)

    def _publish_emotion(self, emotion: str, context: str, intensity: float) -> None:
        payload = json.dumps(
            {"emotion": emotion, "context": context, "intensity": intensity}
        )
        self._emotion_pub.publish(String(data=payload))


def main(args=None):
    rclpy.init(args=args)
    node = WaypointSpeakerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
