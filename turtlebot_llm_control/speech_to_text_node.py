"""Speech-to-text node using Faster-Whisper (offline) with wake-word gating.

In microphone mode, audio is captured via sounddevice, transcribed with
Faster-Whisper, then gated by wake_word.py before publishing to /speech/text.

In mock mode (enable_microphone=false), text is read from /speech/mock_text —
useful for testing without hardware.
"""

import threading
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from turtlebot_llm_control.wake_word import (
    is_alive_request,
    is_emergency_stop_request,
    is_sleep_request,
    is_wake_phrase_only,
    normalize_text,
    strip_wake_phrase,
)


class SpeechToTextNode(Node):
    def __init__(self):
        super().__init__("speech_to_text_node")

        # Parameters
        self.enable_mic = bool(self.declare_parameter("enable_microphone", False).value)
        self.require_wake = bool(self.declare_parameter("require_wake_word", True).value)
        self.wake_window = float(self.declare_parameter("wake_command_window_seconds", 45.0).value)
        self.whisper_size = str(self.declare_parameter("whisper_model", "base").value)
        self.language = str(self.declare_parameter("language", "en").value)
        self.sample_rate = int(self.declare_parameter("sample_rate", 16000).value)
        self.chunk_secs = float(self.declare_parameter("chunk_duration_secs", 3.0).value)

        # Publishers
        self.text_pub = self.create_publisher(String, "/speech/text", 10)
        self.status_pub = self.create_publisher(String, "/speech_to_text/status", 10)
        self.expression_pub = self.create_publisher(String, "/robot/expression", 10)

        # Wake-word state
        self._wake_armed = not self.require_wake
        self._wake_time = 0.0

        # Whisper model (loaded in background thread)
        self._model = None

        if self.enable_mic:
            self._log_status("Loading Faster-Whisper model — please wait…")
            threading.Thread(target=self._load_model_and_start, daemon=True).start()
        else:
            self.create_subscription(String, "/speech/mock_text", self._mock_cb, 10)
            self._log_status("Mock mode active. Publish to /speech/mock_text to inject text.")

        self.get_logger().info(
            f"STT node ready. mic={self.enable_mic} "
            f"wake_word={self.require_wake} model={self.whisper_size}"
        )

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------

    def _log_status(self, msg: str):
        self.status_pub.publish(String(data=msg))
        self.get_logger().info(msg)

    # ------------------------------------------------------------------
    # Microphone + Whisper
    # ------------------------------------------------------------------

    def _load_model_and_start(self):
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self.whisper_size,
                device="cpu",
                compute_type="int8",
            )
            self._log_status(f"Whisper '{self.whisper_size}' model loaded. Listening…")
            threading.Thread(target=self._audio_loop, daemon=True).start()
        except ImportError:
            self.get_logger().error(
                "faster-whisper not installed. Run:  pip install faster-whisper sounddevice"
            )
            self._log_status("ERROR: faster-whisper not installed.")
        except Exception as exc:
            self.get_logger().error(f"Failed to load Whisper model: {exc}")

    def _audio_loop(self):
        try:
            import numpy as np
            import sounddevice as sd
        except ImportError:
            self.get_logger().error("sounddevice/numpy not installed.")
            return

        chunk_samples = int(self.sample_rate * self.chunk_secs)
        self._log_status(
            f"Audio loop started: {self.sample_rate} Hz, {self.chunk_secs}s chunks"
        )

        while rclpy.ok():
            try:
                audio = sd.rec(
                    chunk_samples,
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype="float32",
                    blocking=True,
                )
                audio_1d = audio.flatten()

                # Skip silent chunks
                rms = float(np.sqrt(np.mean(audio_1d ** 2)))
                if rms < 0.005:
                    continue

                segments, _ = self._model.transcribe(
                    audio_1d,
                    language=self.language,
                    vad_filter=True,
                    beam_size=3,
                )
                text = " ".join(s.text for s in segments).strip()
                if text:
                    self.get_logger().info(f"Transcribed: '{text}'")
                    self._process(text)
            except Exception as exc:
                self.get_logger().warning(f"Audio error: {exc}")
                time.sleep(0.5)

    # ------------------------------------------------------------------
    # Mock mode
    # ------------------------------------------------------------------

    def _mock_cb(self, msg: String):
        text = msg.data.strip()
        if text:
            self._process(text)

    # ------------------------------------------------------------------
    # Wake-word gating + publish
    # ------------------------------------------------------------------

    def _process(self, raw: str):
        t = normalize_text(raw)

        # Always allow emergency stop / sleep regardless of gating
        if is_emergency_stop_request(t):
            self._publish("emergency stop")
            return

        if is_sleep_request(t):
            self._wake_armed = False
            self._log_status("Going to sleep mode.")
            self._publish("sleep")
            return

        if not self.require_wake:
            self._publish(t)
            return

        # Wake-word gating
        stripped = strip_wake_phrase(t)
        is_wake = stripped is not None

        if is_wake:
            self._wake_armed = True
            self._wake_time = time.time()
            self.expression_pub.publish(String(data="LISTENING"))
            self._log_status(f"Wake word detected — listening for {self.wake_window:.0f}s")
            command = (stripped or "").strip()
            if not command or is_wake_phrase_only(t):
                self._publish("are you there")
                return
            self._publish(command)
            return

        if self._wake_armed and (time.time() - self._wake_time) < self.wake_window:
            if is_alive_request(t):
                self._publish("are you there")
                return
            self._publish(t)
        else:
            self._wake_armed = False
            self._log_status(f"Ignored (no wake word): '{t}'")

    def _publish(self, text: str):
        self._log_status(f"Publishing: '{text}'")
        self.text_pub.publish(String(data=text))


def main(args=None):
    rclpy.init(args=args)
    node = SpeechToTextNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
