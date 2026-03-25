from std_msgs.msg import String

import rclpy
from rclpy.node import Node

from turtlebot_llm_control.llm_dialogue import LLMDialogueEngine


class SpeechCommandNode(Node):
    def __init__(self):
        super().__init__("speech_command_node")
        self.enable_llm = self.declare_parameter("enable_llm", True).value
        self.llm_provider = self.declare_parameter("llm_provider", "groq").value
        self.llm_model = self.declare_parameter("llm_model", "llama-3.3-70b-versatile").value
        self.llm_api_key_path = self.declare_parameter("llm_api_key_path", "").value
        self.personality = self.declare_parameter(
            "personality",
            (
                "You are Karan's TurtleBot assistant. "
                "You feel like a warm, attentive personal companion in a live voice conversation. "
                "You are friendly, present, lightly playful, emotionally intelligent, and concise. "
                "For normal conversation, reply naturally and keep the exchange flowing. "
                "Only choose an action if the user clearly requested robot behavior."
            ),
        ).value

        self.intent_publisher = self.create_publisher(String, "/speech/intent", 10)
        self.subscription = self.create_subscription(
            String, "/speech/text", self.handle_speech_text, 10
        )
        self.dialogue = LLMDialogueEngine(
            enable_llm=self.enable_llm,
            llm_provider=str(self.llm_provider),
            llm_model=str(self.llm_model),
            llm_api_key_path=str(self.llm_api_key_path),
            personality=str(self.personality),
            warn=lambda message: self.get_logger().warning(message),
        )
        self.get_logger().info(
            "Speech command node ready. enable_llm=%s provider=%s llm_client=%s"
            % (self.enable_llm, self.llm_provider, self.dialogue.client is not None)
        )

    def handle_speech_text(self, msg: String) -> None:
        utterance = msg.data.strip()
        token = self.dialogue.resolve_token(utterance)

        intent_msg = String()
        intent_msg.data = token.to_json()
        self.intent_publisher.publish(intent_msg)
        self.get_logger().info("Recognized intent=%s utterance='%s'" % (token.intent, token.utterance))


def main(args=None):
    rclpy.init(args=args)
    node = SpeechCommandNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
