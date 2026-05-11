from std_msgs.msg import String

import rclpy
from rclpy.node import Node

from turtlebot_llm_control.llm_dialogue import LLMDialogueEngine


class SpeechCommandNode(Node):
    def __init__(self):
        super().__init__("speech_command_node")
        self.enable_llm = self.declare_parameter("enable_llm", True).value
        self.llm_model = self.declare_parameter(
            "llm_model", "qwen2.5:7b"
        ).value
        self.ollama_host = self.declare_parameter(
            "ollama_host", "http://localhost:11434"
        ).value
        self.knowledge_db_path = self.declare_parameter("knowledge_db_path", "").value
        self.personality = self.declare_parameter(
            "personality",
            (
                "You are a TurtleBot social tour guide assistant. "
                "You feel like a warm, attentive personal companion in a live voice conversation. "
                "You are friendly, present, lightly playful, emotionally intelligent, and concise. "
                "For normal conversation, reply naturally and keep the exchange flowing. "
                "Only choose an action if the user clearly requested robot behaviour."
            ),
        ).value

        self.intent_publisher = self.create_publisher(String, "/speech/intent", 10)
        self.subscription = self.create_subscription(
            String, "/speech/text", self.handle_speech_text, 10
        )
        self.dialogue = LLMDialogueEngine(
            enable_llm=bool(self.enable_llm),
            llm_model=str(self.llm_model),
            ollama_host=str(self.ollama_host),
            knowledge_db_path=str(self.knowledge_db_path),
            personality=str(self.personality),
            warn=lambda msg: self.get_logger().warning(msg),
        )
        self.get_logger().info(
            "Speech command node ready. enable_llm=%s model=%s ollama=%s client=%s"
            % (
                self.enable_llm,
                self.llm_model,
                self.ollama_host,
                self.dialogue.client is not None,
            )
        )

    def handle_speech_text(self, msg: String) -> None:
        utterance = msg.data.strip()
        token = self.dialogue.resolve_token(utterance)
        intent_msg = String()
        intent_msg.data = token.to_json()
        self.intent_publisher.publish(intent_msg)
        self.get_logger().info(
            "intent=%s utterance=%r" % (token.intent, token.utterance)
        )


def main(args=None):
    rclpy.init(args=args)
    node = SpeechCommandNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
