"""Rule-based fallback intent parser.

Used by RobotBrain when Ollama is unreachable. Handles the most common
social-guide commands without an LLM.
"""

from turtlebot_llm_control.models import IntentToken
from turtlebot_llm_control.wake_word import (
    is_alive_request,
    is_emergency_stop_request,
    normalize_text,
)


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
    "ten": "10",
}

COMMAND_PREFIXES = (
    "pepper ",
    "aria ",
    "robot ",
    "please ",
    "can you ",
    "could you ",
    "will you ",
)


def _cmd(text: str, *phrases: str) -> bool:
    """Return True if text matches one of the phrases (with optional prefix)."""
    if text in phrases:
        return True
    if any(text.startswith(p + " ") for p in phrases):
        return True
    for prefix in COMMAND_PREFIXES:
        if text.startswith(prefix):
            remainder = text[len(prefix):]
            if remainder in phrases or any(remainder.startswith(p + " ") for p in phrases):
                return True
    return False


def parse_utterance(text: str) -> IntentToken:
    raw = text.strip()
    t = normalize_text(raw)

    if not t:
        return IntentToken(intent="unknown", utterance=raw, response="I didn't catch that.")

    if is_alive_request(t):
        return IntentToken(
            intent="is_alive",
            utterance=raw,
            response="Yes, I'm here and ready to help.",
        )

    if is_emergency_stop_request(t):
        return IntentToken(
            intent="stop",
            utterance=raw,
            response="Emergency stop — stopping everything now.",
        )

    if _cmd(t, "follow", "follow me", "come with me"):
        return IntentToken(
            intent="follow",
            utterance=raw,
            response="Sure, I'll follow you.",
        )

    if _cmd(t, "stop", "halt", "freeze", "stop stop", "stop now"):
        return IntentToken(intent="stop", utterance=raw, response="Stopping now.")

    if _cmd(t, "stop navigation", "cancel navigation"):
        return IntentToken(
            intent="stop_navigation",
            utterance=raw,
            response="Navigation canceled.",
        )

    if _cmd(t, "pause"):
        return IntentToken(intent="pause", utterance=raw, response="Pausing.")

    if _cmd(t, "resume", "continue"):
        return IntentToken(intent="resume", utterance=raw, response="Resuming.")

    # Tour commands — extract tour number/name
    if "start tour" in t or "begin tour" in t or "run tour" in t:
        label = _extract_tour_label(t)
        return IntentToken(
            intent="start_tour",
            label=label,
            utterance=raw,
            response=f"Starting tour {label}.",
        )

    if "go home" in t or "return to dock" in t or "dock" in t:
        return IntentToken(
            intent="dock",
            utterance=raw,
            response="Heading back to the dock.",
        )

    if "save waypoint" in t or "mark this" in t or "save this location" in t or "save position" in t:
        return IntentToken(
            intent="save_waypoint",
            utterance=raw,
            response="Saving current position as a waypoint.",
        )

    if "manual override" in t or "take over" in t or "enable teleop" in t:
        return IntentToken(
            intent="manual_override_on",
            utterance=raw,
            response="Manual override enabled.",
        )

    if "resume autonomous" in t or "disable manual override" in t:
        return IntentToken(
            intent="manual_override_off",
            utterance=raw,
            response="Autonomous mode restored.",
        )

    if _cmd(t, "go to", "navigate to", "take me to"):
        location = _extract_location(t)
        return IntentToken(
            intent="navigate",
            location=location,
            utterance=raw,
            response=f"Navigating to {location}.",
        )

    if "explain" in t or "tell me about" in t or "what is this" in t or "describe" in t:
        location = _extract_location(t) or "this area"
        return IntentToken(
            intent="explain",
            location=location,
            utterance=raw,
            response=f"Let me tell you about {location}.",
        )

    return IntentToken(
        intent="unknown",
        utterance=raw,
        response="I'm not sure what you'd like me to do. Could you rephrase that?",
    )


def _extract_tour_label(text: str) -> str:
    """Extract tour identifier from text like 'start tour one' → '1'."""
    for word, digit in NUMBER_WORDS.items():
        if word in text:
            return digit
    # Look for digits
    parts = text.split()
    for part in parts:
        if part.isdigit():
            return part
    return "1"


def _extract_location(text: str) -> str:
    markers = ["go to ", "navigate to ", "take me to ", "tell me about ", "explain "]
    for marker in markers:
        if marker in text:
            raw_loc = text.split(marker, 1)[1].strip()
            return _normalize_location(raw_loc)
    return "unknown_location"


def _normalize_location(text: str) -> str:
    words = text.split()
    normalized = []
    for word in words:
        word = NUMBER_WORDS.get(word, word)
        normalized.append(word)
    return "_".join(normalized) if normalized else "unknown_location"
