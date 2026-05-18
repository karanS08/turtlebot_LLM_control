"""
Waypoint Recorder
=================
Run alongside teleop. Drive the robot to a location, then press R + Enter
to save the current position to the social_guide waypoint database.

The save is triggered by publishing to /save_tour_command, which social_guide's
tour_saver.py picks up, does a TF lookup, and saves the pose to tours.db.
This package does NOT modify social_guide.

Usage:
  ros2 run tour_maker waypoint_recorder
"""

import threading

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from std_msgs.msg import String


class WaypointRecorder(Node):
    def __init__(self):
        super().__init__("waypoint_recorder")

        # Publisher that triggers tour_saver.py in social_guide
        self.save_pub = self.create_publisher(String, "/save_tour_command", 10)

        self._x = 0.0
        self._y = 0.0
        self._save_count = 0

        self.create_subscription(
            PoseWithCovarianceStamped,
            "/amcl_pose",
            self._pose_cb,
            10,
        )

        self.get_logger().info("Waypoint Recorder ready.")
        self._print_banner()
        threading.Thread(target=self._keyboard_loop, daemon=True).start()

    def _pose_cb(self, msg: PoseWithCovarianceStamped):
        self._x = msg.pose.pose.position.x
        self._y = msg.pose.pose.position.y

    def _print_banner(self):
        print("\n" + "=" * 60)
        print("  WAYPOINT RECORDER — Social Tour Guide Robot")
        print("=" * 60)
        print("  Drive the robot to a location using teleop.")
        print("  Press  R  + Enter  to save the current position.")
        print("  Press  Q  + Enter  to quit.")
        print("=" * 60 + "\n")

    def _keyboard_loop(self):
        while rclpy.ok():
            try:
                line = input(
                    f"  Robot at ({self._x:.2f}, {self._y:.2f})  →  "
                ).strip().lower()
            except (EOFError, KeyboardInterrupt):
                break

            if line == "r":
                self.save_pub.publish(String(data="save"))
                self._save_count += 1
                print(
                    f"  ✓ Waypoint #{self._save_count} saved at "
                    f"({self._x:.2f}, {self._y:.2f})\n"
                )
            elif line == "q":
                print("  Shutting down waypoint recorder.")
                self.get_logger().info("User quit waypoint recorder.")
                break
            elif line == "":
                pass
            else:
                print("  Unknown key. Press R to save, Q to quit.\n")


def main(args=None):
    rclpy.init(args=args)
    node = WaypointRecorder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
