import time
from typing import Optional

import cv2
import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import String

from turtlebot_llm_control.color_tracking import detect_color_targets, draw_detection_debug


class FollowMeNode(Node):
    def __init__(self):
        super().__init__("follow_me_node")
        self.use_compressed = self.declare_parameter("use_compressed", False).value
        self.image_topic = self.declare_parameter(
            "image_topic", "/camera/image_raw/compressed" if self.use_compressed else "/camera/image_raw"
        ).value
        self.publish_debug_view = self.declare_parameter("publish_debug_view", True).value
        self.default_target_color = self.declare_parameter("default_target_color", "yellow").value
        self.rcv_timeout_secs = self.declare_parameter("rcv_timeout_secs", 1.0).value
        self.angular_chase_multiplier = self.declare_parameter("angular_chase_multiplier", 0.8).value
        self.forward_chase_speed = self.declare_parameter("forward_chase_speed", 0.12).value
        self.search_angular_speed = self.declare_parameter("search_angular_speed", 0.45).value
        self.max_size_thresh = self.declare_parameter("max_size_thresh", 0.24).value
        self.filter_value = self.declare_parameter("filter_value", 0.85).value
        self.search_window = [
            int(self.declare_parameter("x_min", 0).value),
            int(self.declare_parameter("y_min", 0).value),
            int(self.declare_parameter("x_max", 100).value),
            int(self.declare_parameter("y_max", 100).value),
        ]

        self.active = False
        self.target_color = self.default_target_color
        self.target_val = 0.0
        self.target_size = 0.0
        self.lastrcvtime = time.time() - 10000.0

        self.control_subscription = self.create_subscription(
            String, "/follow_me/control", self.handle_control, 10
        )
        if self.use_compressed:
            self.image_subscription = self.create_subscription(
                CompressedImage, self.image_topic, self.handle_compressed_image, 10
            )
        else:
            self.image_subscription = self.create_subscription(
                Image, self.image_topic, self.handle_raw_image, 10
            )

        self.cmd_publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.status_publisher = self.create_publisher(String, "/follow_me/status", 10)
        self.debug_publisher = self.create_publisher(CompressedImage, "/follow_me/debug/compressed", 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info(
            "Follow-me node ready. image_topic=%s default_target_color=%s"
            % (self.image_topic, self.default_target_color)
        )

    def handle_control(self, msg: String) -> None:
        command = msg.data.strip().lower()
        if command == "stop":
            self.active = False
            self.publish_cmd(0.0, 0.0)
            self.publish_status("Follow mode stopped.")
            return

        if command.startswith("start"):
            parts = command.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                self.target_color = parts[1].strip()
            else:
                self.target_color = self.default_target_color
            self.active = True
            self.lastrcvtime = time.time() - 10000.0
            self.publish_status("Follow mode started for %s target." % self.target_color)
            return

        if command.startswith("color:"):
            color = command.split(":", 1)[1].strip()
            if color:
                self.target_color = color
                self.publish_status("Follow target color set to %s." % self.target_color)
            return

        self.publish_status("Unknown follow command: %s" % command)

    def handle_raw_image(self, msg: Image) -> None:
        if not self.active:
            return
        bgr_image = self.image_to_bgr(msg)
        if bgr_image is None:
            return
        self.process_frame(bgr_image, msg.header.stamp.sec, msg.header.stamp.nanosec)

    def handle_compressed_image(self, msg: CompressedImage) -> None:
        if not self.active:
            return
        np_arr = np.frombuffer(msg.data, np.uint8)
        bgr_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if bgr_image is None:
            self.publish_status("Failed to decode compressed follow image.")
            return
        self.process_frame(bgr_image, 0, 0)

    def process_frame(self, bgr_image: np.ndarray, sec: int, nanosec: int) -> None:
        detections, _, combined_mask = detect_color_targets(
            bgr_image,
            color_names=[self.target_color],
            search_window=self.search_window,
        )

        if detections:
            detection = detections[0]
            f = float(self.filter_value)
            self.target_val = self.target_val * f + detection.normalized_x * (1.0 - f)
            self.target_size = self.target_size * f + detection.normalized_size * (1.0 - f)
            self.lastrcvtime = time.time()
            self.publish_status(
                "Tracking %s target offset=%.2f size=%.2f"
                % (self.target_color, self.target_val, self.target_size)
            )

        if self.publish_debug_view:
            debug_image = draw_detection_debug(
                bgr_image,
                detections[:1],
                combined_mask,
                search_window=self.search_window,
            )
            self.publish_debug_image(debug_image, sec, nanosec)

    def timer_callback(self) -> None:
        if not self.active:
            return

        if time.time() - self.lastrcvtime < float(self.rcv_timeout_secs):
            linear = self.forward_chase_speed if self.target_size < self.max_size_thresh else 0.0
            angular = -self.angular_chase_multiplier * self.target_val
            self.publish_cmd(linear, angular)
            return

        self.publish_cmd(0.0, self.search_angular_speed)

    def image_to_bgr(self, msg: Image) -> Optional[np.ndarray]:
        channels = 3 if msg.encoding in {"rgb8", "bgr8"} else 4 if msg.encoding in {"rgba8", "bgra8"} else 0
        if channels == 0:
            self.publish_status("Unsupported image encoding: %s" % msg.encoding)
            return None

        frame = np.frombuffer(msg.data, dtype=np.uint8)
        frame = frame.reshape((msg.height, msg.width, channels))

        if msg.encoding == "rgb8":
            return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if msg.encoding == "rgba8":
            return cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        if msg.encoding == "bgra8":
            return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame.copy()

    def publish_debug_image(self, debug_image: np.ndarray, sec: int, nanosec: int) -> None:
        success, encoded = cv2.imencode(".jpg", debug_image)
        if not success:
            self.publish_status("Failed to encode follow debug image.")
            return

        msg = CompressedImage()
        msg.header.stamp.sec = sec
        msg.header.stamp.nanosec = nanosec
        msg.format = "jpeg"
        msg.data = encoded.tobytes()
        self.debug_publisher.publish(msg)

    def publish_cmd(self, linear_x: float, angular_z: float) -> None:
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)
        self.cmd_publisher.publish(msg)

    def publish_status(self, text: str) -> None:
        msg = String()
        msg.data = text
        self.status_publisher.publish(msg)
        self.get_logger().info(text)


def main(args=None):
    rclpy.init(args=args)
    node = FollowMeNode()
    try:
        rclpy.spin(node)
    finally:
        node.publish_cmd(0.0, 0.0)
        node.destroy_node()
        rclpy.shutdown()
