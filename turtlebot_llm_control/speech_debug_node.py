import json

from std_msgs.msg import String

import rclpy
from rclpy.node import Node

# ANSI colour codes — safe in any ROS2 screen output terminal
_R = "\033[91m"   # red
_G = "\033[92m"   # green
_Y = "\033[93m"   # yellow
_C = "\033[96m"   # cyan
_M = "\033[95m"   # magenta
_B = "\033[94m"   # blue
_W = "\033[97m"   # white
_X = "\033[0m"    # reset
_BOLD = "\033[1m"

_DIVIDER = f"{_B}{'─' * 60}{_X}"


class SpeechDebugNode(Node):
    """
    Aggregates all speech pipeline topics and prints a live, colour-coded
    trace to the terminal.  Also republishes as /speech/debug for rosbag.

    Topics monitored:
      /speech_to_text/status  — STT system status
      /speech/text            — what the robot heard (after wake-word gate)
      /speech/intent          — parsed intent JSON from the LLM brain
      /speech/response        — text the robot is about to speak
      /robot/expression       — current robot expression state
    """

    def __init__(self):
        super().__init__("speech_debug_node")
        self.pub = self.create_publisher(String, "/speech/debug", 20)

        subs = [
            ("/speech_to_text/status", self._on_stt_status),
            ("/speech/text",           self._on_heard),
            ("/speech/intent",         self._on_intent),
            ("/speech/response",       self._on_response),
            ("/robot/expression",      self._on_expression),
        ]
        for topic, cb in subs:
            self.create_subscription(String, topic, cb, 20)

        print(f"\n{_BOLD}{_W}{'═' * 60}{_X}")
        print(f"{_BOLD}{_W}  ARIA Speech Debug Monitor{_X}")
        print(f"{_BOLD}{_W}  Topics: /speech/text  /speech/intent  /speech/response{_X}")
        print(f"{_BOLD}{_W}  Also publishing to: /speech/debug{_X}")
        print(f"{_BOLD}{_W}{'═' * 60}{_X}\n")

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_stt_status(self, msg: String):
        self._relay("stt_status", msg.data)
        print(f"{_DIVIDER}")
        print(f"  {_B}[STT]{_X} {msg.data}")

    def _on_heard(self, msg: String):
        self._relay("heard", msg.data)
        print(f"{_DIVIDER}")
        print(f"  {_G}{_BOLD}[HEARD ]{_X}  {_W}{msg.data}{_X}")

    def _on_intent(self, msg: String):
        self._relay("intent", msg.data)
        # Pretty-print the intent JSON
        try:
            d = json.loads(msg.data)
            intent = d.get("intent", "?")
            label = d.get("label", "")
            conf_raw = d.get("metadata", {})
            if isinstance(conf_raw, dict):
                conf = conf_raw.get("confidence", "?")
            else:
                conf = "?"
            reasoning = ""
            if isinstance(conf_raw, dict):
                reasoning = conf_raw.get("reasoning", "")
            print(f"  {_Y}{_BOLD}[INTENT]{_X}  intent={_W}{intent}{_X}  "
                  f"label={_W}{label}{_X}  conf={_W}{conf}{_X}")
            if reasoning:
                short = reasoning[:120] + ("…" if len(reasoning) > 120 else "")
                print(f"           {_Y}reason:{_X} {short}")
        except Exception:
            print(f"  {_Y}[INTENT]{_X} {msg.data}")

    def _on_response(self, msg: String):
        self._relay("response", msg.data)
        print(f"  {_C}{_BOLD}[ARIA  ]{_X}  {_W}\"{msg.data}\"{_X}")
        print()

    def _on_expression(self, msg: String):
        self._relay("expression", msg.data)
        _EXPR_COLOR = {
            "THINKING": _Y, "TALKING": _C, "EXPLAINING": _M,
            "NAVIGATING": _B, "LISTENING": _G, "IDLE": _W,
        }
        color = _EXPR_COLOR.get(msg.data, _W)
        print(f"  {color}[STATE  ]  {msg.data}{_X}")

    # ------------------------------------------------------------------
    # Republish helper
    # ------------------------------------------------------------------

    def _relay(self, label: str, data: str):
        out = String()
        out.data = f"[{label}] {data}"
        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = SpeechDebugNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
