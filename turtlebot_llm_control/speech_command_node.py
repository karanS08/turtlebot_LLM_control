import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from turtlebot_llm_control.llm_brain import RobotBrain


class SpeechCommandNode(Node):
    def __init__(self):
        super().__init__("speech_command_node")

        self.enable_llm = self.declare_parameter("enable_llm", True).value
        self.ollama_model = str(self.declare_parameter("ollama_model", "qwen2.5").value)
        self.ollama_url = str(
            self.declare_parameter("ollama_url", "http://localhost:11434/api/chat").value
        )
        self.memory_file = str(
            self.declare_parameter("memory_file", "~/.ros/robot_memory.json").value
        )

        self.intent_pub = self.create_publisher(String, "/speech/intent", 10)
        self.expression_pub = self.create_publisher(String, "/robot/expression", 10)

        self.create_subscription(String, "/speech/text", self._on_speech, 10)
        self.create_subscription(String, "/tour/status", self._on_tour_status, 10)

        self._latest_context: dict = {}

        if self.enable_llm:
            self.brain = RobotBrain(
                ollama_model=self.ollama_model,
                ollama_url=self.ollama_url,
                memory_file=self.memory_file,
                warn=self.get_logger().warning,
                info=self.get_logger().info,
            )
        else:
            self.brain = RobotBrain(
                ollama_model=self.ollama_model,
                ollama_url="http://localhost:1",  # unreachable → rule-only mode
                memory_file=self.memory_file,
                warn=self.get_logger().warning,
                info=self.get_logger().info,
            )

        self.get_logger().info(
            f"Speech command node ready. ollama_model={self.ollama_model}"
        )

    def _on_tour_status(self, msg: String):
        try:
            self._latest_context = json.loads(msg.data)
        except Exception:
            pass

    def _pub_expression(self, state: str):
        self.expression_pub.publish(String(data=state))

    def _on_speech(self, msg: String):
        utterance = msg.data.strip()
        if not utterance:
            return

        self._pub_expression("THINKING")

        token = self.brain.think(utterance, self._latest_context)

        intent_msg = String()
        intent_msg.data = token.to_json()
        self.intent_pub.publish(intent_msg)

        self._pub_expression("TALKING")
        self.get_logger().info(f"intent={token.intent} utterance='{utterance}'")

    def destroy_node(self):
        try:
            self.brain.summarize_and_save_session()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SpeechCommandNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
