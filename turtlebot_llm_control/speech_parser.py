from turtlebot_llm_control.models import IntentToken
from turtlebot_llm_control.wake_word import (
    is_alive_request,
    is_emergency_stop_request,
    normalize_text,
)


COLOR_NAMES = ("red", "green", "blue", "yellow")
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
COMMAND_PREFIXES = (
    "pepper ",
    "robot ",
    "please ",
    "can you ",
    "could you ",
    "will you ",
)


def is_direct_command(text: str, *phrases: str) -> bool:
    if text in phrases:
        return True
    if any(text.startswith(phrase + " ") for phrase in phrases):
        return True
    for prefix in COMMAND_PREFIXES:
        remainder = text[len(prefix) :] if text.startswith(prefix) else ""
        if not remainder:
            continue
        if remainder in phrases:
            return True
        if any(remainder.startswith(phrase + " ") for phrase in phrases):
            return True
    return False


def parse_utterance(text: str) -> IntentToken:
    raw = text.strip()
    cleaned = normalize_text(raw)

    if not cleaned:
        return IntentToken(intent="unknown", utterance=raw, response="I did not catch that.")

    if is_alive_request(cleaned):
        return IntentToken(
            intent="is_alive",
            utterance=raw,
            response="Yes, I am here, awake, and ready to help.",
        )

    if is_emergency_stop_request(cleaned):
        return IntentToken(
            intent="stop",
            utterance=raw,
            response="Emergency stop. Stopping everything now.",
        )

    if (("here is" in cleaned or "this is" in cleaned or "look at" in cleaned) and "bin" in cleaned):
        color = extract_color(cleaned) or "green"
        return IntentToken(
            intent="inspect_bin",
            utterance=raw,
            response="Okay, I am looking for the {} bin now.".format(color),
            metadata={"bin_color": color},
        )

    if is_direct_command(cleaned, "follow", "follow me", "come with me"):
        color = extract_color(cleaned) or "yellow"
        return IntentToken(
            intent="follow",
            utterance=raw,
            response="Starting follow mode for the {} target.".format(color),
            metadata={"target_color": color},
        )

    if (
        "manual override" in cleaned
        or "manual control" in cleaned
        or "enable teleop" in cleaned
        or "take over" in cleaned
    ):
        return IntentToken(
            intent="manual_override_on",
            utterance=raw,
            response="Manual override enabled. You can teleoperate now.",
        )

    if is_direct_command(cleaned, "stop navigation", "cancel navigation"):
        return IntentToken(
            intent="stop_navigation",
            utterance=raw,
            response="Stopping navigation now.",
        )

    if (
        "resume autonomous" in cleaned
        or "resume exploration" in cleaned
        or "disable manual override" in cleaned
        or "return to autonomous" in cleaned
    ):
        return IntentToken(
            intent="manual_override_off",
            utterance=raw,
            response="Manual override cleared. Autonomous behavior can resume.",
        )

    if is_direct_command(cleaned, "start exploring", "explore", "search for bins"):
        return IntentToken(
            intent="start_exploration",
            utterance=raw,
            response="Starting autonomous exploration for colored bins.",
        )

    if is_direct_command(cleaned, "stop exploring", "stop exploration"):
        return IntentToken(
            intent="stop_exploration",
            utterance=raw,
            response="Stopping autonomous exploration.",
        )

    if is_direct_command(cleaned, "stop", "halt", "freeze", "stop stop", "stop now"):
        return IntentToken(intent="stop", utterance=raw, response="Stopping the current activity.")

    if is_direct_command(cleaned, "pause"):
        return IntentToken(intent="pause", utterance=raw, response="Pausing for you now.")

    if is_direct_command(cleaned, "resume"):
        return IntentToken(intent="resume", utterance=raw, response="Resuming the previous task.")

    if is_direct_command(cleaned, "start tour", "begin tour"):
        return IntentToken(intent="start_tour", utterance=raw, response="Starting the tour.")

    if is_direct_command(cleaned, "record route", "start recording"):
        label = extract_label(cleaned, fallback="new_route")
        return IntentToken(
            intent="start_recording",
            label=label,
            utterance=raw,
            response="Recording route {}.".format(label),
        )

    if is_direct_command(cleaned, "stop recording"):
        return IntentToken(intent="stop_recording", utterance=raw, response="Route recording stopped.")

    if is_direct_command(cleaned, "save route"):
        label = extract_label(cleaned, fallback="saved_route")
        return IntentToken(
            intent="save_route",
            label=label,
            utterance=raw,
            response="Saving route as {}.".format(label),
        )

    if is_direct_command(cleaned, "replay", "run route"):
        label = extract_label(cleaned, fallback="saved_route")
        return IntentToken(
            intent="replay_route",
            label=label,
            utterance=raw,
            response="Replaying route {}.".format(label),
        )

    if is_direct_command(cleaned, "go to", "navigate to", "take me to"):
        bin_label, bin_color = extract_bin_label(cleaned)
        if "bin" in cleaned:
            return IntentToken(
                intent="go_to_bin",
                label=bin_label,
                utterance=raw,
                response="Navigating to remembered {}.".format(bin_label or "{} bin".format(bin_color)),
                metadata={"bin_color": bin_color},
            )
        location = extract_location(cleaned)
        normalized_full_text = normalize_location_name(cleaned)
        if location == "unknown_location" and "pillar" in normalized_full_text:
            return IntentToken(
                intent="no_action",
                utterance=raw,
                response="I need a pillar number. Please say a pillar from 1 to 9.",
            )
        return IntentToken(
            intent="navigate",
            location=location,
            utterance=raw,
            response="Navigating to {}.".format(location),
        )

    if "explain" in cleaned or "tell me about" in cleaned:
        location = extract_location(cleaned)
        return IntentToken(
            intent="explain",
            location=location,
            utterance=raw,
            response="Preparing an explanation for {}.".format(location),
        )

    return IntentToken(
        intent="unknown",
        utterance=raw,
        response="I understood speech, but I need a clearer command.",
    )


def extract_label(text: str, fallback: str) -> str:
    markers = ["as ", "route ", "called ", "named "]
    for marker in markers:
        if marker in text:
            candidate = text.split(marker, 1)[1].strip().replace(" ", "_")
            if candidate:
                return candidate
    return fallback


def extract_location(text: str) -> str:
    markers = ["go to ", "navigate to ", "take me to ", "tell me about ", "explain "]
    for marker in markers:
        if marker in text:
            candidate = normalize_location_name(text.split(marker, 1)[1].strip())
            if candidate:
                return candidate
    return "unknown_location"


def normalize_location_name(text: str) -> str:
    words = text.split()
    normalized_words = [
        NUMBER_WORDS.get(LOCATION_ALIASES.get(word, word), LOCATION_ALIASES.get(word, word))
        for word in words
    ]
    if normalized_words in (["pillar"], ["pillar", "number"]):
        return ""
    if len(normalized_words) >= 2 and normalized_words[0] == "pillar" and normalized_words[1].isdigit():
        return "pillar_{}".format(normalized_words[1])
    joined = "_".join(normalized_words)
    if joined.startswith("pillar") and joined[6:].isdigit():
        return "pillar_{}".format(joined[6:])
    return joined


def extract_bin_label(text: str) -> tuple[str, str]:
    color = extract_color(text)
    if "bin" not in text:
        return "", color

    digits = ""
    start_collecting = False
    for char in text:
        if char.isdigit():
            digits += char
            start_collecting = True
        elif start_collecting:
            break

    if color and digits:
        return "{}_bin_{:02d}".format(color, int(digits)), color
    if digits:
        return "bin_{:02d}".format(int(digits)), color
    if color:
        return "", color
    return "", ""


def extract_color(text: str) -> str:
    for color in COLOR_NAMES:
        if color in text:
            return color
    return ""
