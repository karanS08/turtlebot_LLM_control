from std_msgs.msg import String

import rclpy
from rclpy.node import Node

from turtlebot_llm_control.audio_utils import speak_text


class SpeechResponseNode(Node):
    def __init__(self):
        super().__init__("speech_response_node")
        self.mute = bool(self.declare_parameter("mute", False).value)
        self.subscription = self.create_subscription(
            String, "/speech/response", self.handle_response, 10
        )
        self.get_logger().info("Speech response node ready. mute=%s" % self.mute)

    def handle_response(self, msg: String) -> None:
        text = msg.data.strip()
        if self.mute or not text:
            return
        if not speak_text(text):
            self.get_logger().warning(
                "No local TTS command available. Install spd-say, espeak, or say to hear responses."
            )


def main(args=None):
    rclpy.init(args=args)
    node = SpeechResponseNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
