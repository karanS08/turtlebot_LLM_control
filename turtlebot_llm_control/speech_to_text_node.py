from difflib import get_close_matches
from time import monotonic
from typing import Optional

from std_msgs.msg import String

import rclpy
from rclpy.node import Node

from turtlebot_llm_control.audio_utils import suppress_stderr
from turtlebot_llm_control.predefined_commands import PREDEFINED_COMMANDS
from turtlebot_llm_control.wake_word import canonicalize_robot_name
from turtlebot_llm_control.wake_word import (
    is_emergency_stop_request,
    is_sleep_request,
    strip_wake_phrase,
)


class SpeechToTextNode(Node):
    def __init__(self):
        super().__init__("speech_to_text_node")
        self.enable_microphone = self.declare_parameter("enable_microphone", False).value
        self.energy_threshold = int(self.declare_parameter("energy_threshold", 300).value)
        self.dynamic_energy_threshold = self.declare_parameter("dynamic_energy_threshold", True).value
        self.phrase_time_limit = float(self.declare_parameter("phrase_time_limit", 3.0).value)
        self.require_wake_word = bool(self.declare_parameter("require_wake_word", True).value)
        self.wake_command_window_seconds = float(
            self.declare_parameter("wake_command_window_seconds", 45.0).value
        )

        self.text_publisher = self.create_publisher(String, "/speech/text", 10)
        self.status_publisher = self.create_publisher(String, "/speech_to_text/status", 10)
        self.mock_subscription = self.create_subscription(
            String, "/speech/mock_text", self.handle_mock_text, 10
        )

        self.recognizer = None
        self.microphone = None
        self.stop_background_listener = None
        self.wake_active_until = 0.0

        if self.enable_microphone:
            self.setup_microphone_listener()
        else:
            self.publish_status("Speech-to-text node ready in mock mode. Publish on /speech/mock_text.")

    def setup_microphone_listener(self) -> None:
        try:
            import speech_recognition as sr
        except ImportError:
            self.publish_status(
                "speech_recognition is not installed. Falling back to /speech/mock_text input."
            )
            return

        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.dynamic_energy_threshold = bool(self.dynamic_energy_threshold)
            with suppress_stderr():
                self.microphone = sr.Microphone()
        except Exception as exc:
            self.publish_status("Failed to initialize microphone STT: %s" % exc)
            return

        with suppress_stderr(), self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)

        self.stop_background_listener = self.recognizer.listen_in_background(
            self.microphone,
            self.handle_audio,
            phrase_time_limit=self.phrase_time_limit,
        )
        self.publish_status("Speech-to-text microphone listener started.")

    def handle_audio(self, recognizer, audio) -> None:
        transcript = self.transcribe_audio(recognizer, audio)
        if not transcript:
            return
        self.process_recognized_text(transcript)

    def transcribe_audio(self, recognizer, audio) -> str:
        try:
            raw_text = recognizer.recognize_google(audio)
        except Exception as exc:
            error_text = str(exc).strip()
            if error_text:
                self.publish_status("Speech recognition failed: %s" % error_text)
            else:
                self.publish_status("Speech recognition could not understand the audio.")
            return ""

        normalized = raw_text.strip().lower()
        if not normalized:
            return ""
        return normalized

    def find_best_command(self, text: str) -> Optional[str]:
        if self.should_skip_fuzzy_match(text):
            return None
        matches = get_close_matches(text, PREDEFINED_COMMANDS, n=1, cutoff=0.6)
        return matches[0] if matches else None

    def should_skip_fuzzy_match(self, text: str) -> bool:
        normalized = canonicalize_robot_name(text)
        multiword_phrases = (
            "go to ",
            "navigate to ",
            "take me to ",
            "tell me about ",
            "explain ",
            "pillar ",
            "pillow ",
            "below ",
        )
        if any(phrase in normalized for phrase in multiword_phrases):
            return True
        return len(normalized.split()) > 2

    def handle_mock_text(self, msg: String) -> None:
        normalized = msg.data.strip().lower()
        if not normalized:
            return
        self.process_recognized_text(normalized)

    def process_recognized_text(self, text: str) -> None:
        gated_text = self.apply_wake_word_gate(text)
        if not gated_text:
            return

        exact_match = next((cmd for cmd in PREDEFINED_COMMANDS if cmd == gated_text), None)
        if exact_match:
            self.publish_recognized_text(exact_match)
            return

        close_match = self.find_best_command(gated_text)
        if close_match:
            self.publish_status("Recognized '%s' as '%s'." % (gated_text, close_match))
            self.publish_recognized_text(close_match)
            return

        self.publish_status("Heard '%s' but it is not in the predefined command set." % gated_text)
        self.publish_recognized_text(gated_text)

    def apply_wake_word_gate(self, text: str) -> str:
        normalized = text.strip().lower()
        if not normalized:
            return ""
        if not self.require_wake_word:
            return normalized
        if is_emergency_stop_request(normalized):
            self.wake_active_until = 0.0
            self.publish_status("Emergency stop detected. Stopping active tasks immediately.")
            return "stop"
        if is_sleep_request(normalized):
            self.wake_active_until = 0.0
            self.publish_status("Sleep command detected. Stopping active tasks and returning to sleep.")
            return "stop"

        wake_command = strip_wake_phrase(normalized)
        now = monotonic()
        if wake_command is not None:
            self.wake_active_until = now + self.wake_command_window_seconds
            if wake_command:
                self.publish_status("Wake phrase detected. Processing '%s'." % wake_command)
                return wake_command
            self.publish_status(
                "Wake phrase detected. Pepper is awake for %.0f seconds."
                % self.wake_command_window_seconds
            )
            return ""

        if now <= self.wake_active_until:
            self.wake_active_until = now + self.wake_command_window_seconds
            return normalized

        self.publish_status(
            "Ignored speech until wake phrase like 'hey', 'hi', 'hello', or 'hey pepper' is heard."
        )
        return ""

    def publish_recognized_text(self, text: str) -> None:
        msg = String()
        msg.data = text
        self.text_publisher.publish(msg)
        self.publish_status("Published recognized text: %s" % text)

    def publish_status(self, text: str) -> None:
        msg = String()
        msg.data = text
        self.status_publisher.publish(msg)
        self.get_logger().info(text)

    def shutdown_listener(self) -> None:
        if self.stop_background_listener is not None:
            self.stop_background_listener(wait_for_stop=False)
            self.stop_background_listener = None


def main(args=None):
    rclpy.init(args=args)
    node = SpeechToTextNode()
    try:
        rclpy.spin(node)
    finally:
        node.shutdown_listener()
        node.destroy_node()
        rclpy.shutdown()
