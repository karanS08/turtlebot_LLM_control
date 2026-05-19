from dataclasses import asdict, dataclass, field
from typing import Dict

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
from rclpy.node import Node
from std_msgs.msg import String


NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}
LOCATION_ALIASES = {
    "pillow": "pillar",
    "below": "pillar",
    "pillar": "pillar",
}
LOCATION_DICT = {
    "pillar_1": (-1.6, -1.1),
    "pillar_2": (-1.6, 0.0),
    "pillar_3": (-1.6, 1.1),
    "pillar_4": (-0.5, -1.1),
    "pillar_5": (-0.5, 0.0),
    "pillar_6": (-0.5, 1.1),
    "pillar_7": (0.6, -1.1),
    "pillar_8": (0.6, 0.0),
    "pillar_9": (0.6, 1.1),
}


@dataclass
class IntentToken:
    intent: str
    label: str = ""
    location: str = ""
    utterance: str = ""
    response: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_json(cls, payload: str) -> "IntentToken":
        import json

        data = json.loads(payload)
        return cls(**data)

    def to_json(self) -> str:
        import json

        return json.dumps(asdict(self))


class NavigationSpeech(Node):
    def __init__(self):
        super().__init__("speech_listener")
        self.create_subscription(String, "/speech/intent", self.callback_, 10)
        self.nav = BasicNavigator()
        self.nav.waitUntilNav2Active()

    def callback_(self, msg: String) -> None:
        token = self._decode_token(msg.data)
        location_name = self._resolve_location(token)
        if location_name not in LOCATION_DICT:
            self.get_logger().info(
                'Ignoring intent="%s" location="%s"' % (token.intent, location_name)
            )
            return

        x_goal, y_goal = LOCATION_DICT[location_name]
        goal = PoseStamped()
        goal.header.frame_id = "map"
        goal.header.stamp = self.nav.get_clock().now().to_msg()
        goal.pose.position.x = x_goal
        goal.pose.position.y = y_goal
        goal.pose.orientation.w = 1.0
        self.get_logger().info("Trying to go to %s" % location_name)
        self.nav.goToPose(goal)

    def _decode_token(self, payload: str) -> IntentToken:
        try:
            return IntentToken.from_json(payload)
        except Exception:
            return IntentToken(
                intent="navigate",
                location=self._normalize_location_name(payload.strip().lower()),
                utterance=payload,
            )

    def _resolve_location(self, token: IntentToken) -> str:
        if token.intent != "navigate":
            return ""
        candidate = token.location or token.label or token.utterance
        return self._normalize_location_name(str(candidate).strip().lower())

    def _normalize_location_name(self, text: str) -> str:
        words = text.split()
        normalized_words = [
            NUMBER_WORDS.get(LOCATION_ALIASES.get(word, word), LOCATION_ALIASES.get(word, word))
            for word in words
        ]
        if normalized_words in (["pillar"], ["pillar", "number"]):
            return ""
        if (
            len(normalized_words) >= 2
            and normalized_words[0] == "pillar"
            and normalized_words[1].isdigit()
        ):
            return "pillar_{}".format(normalized_words[1])
        joined = "_".join(normalized_words)
        if joined.startswith("pillar") and joined[6:].isdigit():
            return "pillar_{}".format(joined[6:])
        return joined


def main(args=None):
    rclpy.init(args=args)
    node = NavigationSpeech()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
