"""
RobotBrain — offline LLM intent engine using Ollama (Qwen2.5).

Replaces llm_dialogue.py. Provides chain-of-thought JSON reasoning so the
robot understands fuzzy / natural language requests and maps them to structured
IntentTokens that the behaviour tree can act on.

Falls back to rule-based speech_parser if Ollama is unreachable.
"""

import json
import urllib.error
import urllib.request
from typing import Callable, Optional

from turtlebot_llm_control.memory_manager import MemoryManager
from turtlebot_llm_control.models import IntentToken
from turtlebot_llm_control.speech_parser import parse_utterance


# ---------------------------------------------------------------------------
# Static capability description — injected into every system prompt
# ---------------------------------------------------------------------------

_CAPABILITIES = """\
You are SALVAE, a friendly and warm social tour guide robot. You speak naturally \
and concisely because your responses are spoken aloud.

WHAT YOU CAN DO:
  navigate     → travel to a named waypoint or location (by number, name, or nickname)
  start_tour   → run a saved tour (tour1, tour2, …) visiting waypoints in order with spoken descriptions
  save_waypoint → save the robot's current position as a new named waypoint
  explain      → describe what is at the current or a named location
  follow       → start following a person around
  stop         → stop all movement immediately
  pause        → pause current activity (can be resumed later)
  resume       → resume the previously paused activity
  dock         → return to home base / charging station
  is_alive     → respond to "are you there / can you hear me" checks
  no_action    → chat naturally without triggering any robot behaviour

WHAT YOU CANNOT DO:
  - Access the internet or external websites
  - Control physical doors, lights, or other infrastructure
  - Carry objects
  If asked something outside your abilities, say so warmly and suggest what you CAN do.

RULES:
  - If the request is close to a capability, do it — be smart about synonyms and nicknames.
  - Reason step-by-step inside the "reasoning" field before choosing an intent.
  - Keep "response" natural, warm, concise — it will be spoken aloud.
  - If confidence < 0.6, set intent to "no_action" and ask a clarifying question in "response".
  - Output ONLY valid JSON matching the schema below. No markdown, no extra text.

JSON SCHEMA (always output exactly this structure):
{
  "reasoning": "<step-by-step thinking>",
  "intent": "<navigate|start_tour|save_waypoint|explain|follow|stop|pause|resume|dock|is_alive|no_action>",
  "label": "<tour name, waypoint name/number, or empty string>",
  "location": "<location name if navigating, else empty string>",
  "confidence": <0.0 to 1.0>,
  "response": "<what ARIA says aloud>"
}"""


class RobotBrain:
    """LLM-powered intent resolver with persistent memory and rule-based fallback."""

    def __init__(
        self,
        ollama_model: str = "qwen2.5",
        ollama_url: str = "http://localhost:11434/api/chat",
        memory_file: str = "~/.ros/robot_memory.json",
        timeout: float = 8.0,
        warn: Optional[Callable[[str], None]] = None,
        info: Optional[Callable[[str], None]] = None,
    ):
        self.model = ollama_model
        self.url = ollama_url
        self.timeout = timeout
        self.memory = MemoryManager(memory_file)
        self._warn = warn or print
        self._info = info or print
        self._ollama_ok = self._ping_ollama()

    # ------------------------------------------------------------------
    # Ollama helpers
    # ------------------------------------------------------------------

    def _ping_ollama(self) -> bool:
        try:
            tags_url = self.url.replace("/api/chat", "/api/tags")
            urllib.request.urlopen(
                urllib.request.Request(tags_url, method="GET"), timeout=3
            )
            self._info("Ollama reachable — LLM brain active")
            return True
        except Exception:
            self._warn("Ollama not reachable — running in rule-based fallback mode")
            return False

    def _call_ollama(self, messages: list[dict]) -> str:
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "format": "json",
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            self.url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read())["message"]["content"]

    # ------------------------------------------------------------------
    # System prompt
    # ------------------------------------------------------------------

    def _build_system(self, context: dict) -> str:
        parts = [_CAPABILITIES]

        state = context.get("current_state", "IDLE")
        tours = context.get("available_tours", [])
        waypoints = context.get("available_waypoints", [])

        status_lines = [f"CURRENT STATE: {state}"]
        if tours:
            status_lines.append(f"AVAILABLE TOURS: {', '.join(tours)}")
        if waypoints:
            status_lines.append("AVAILABLE WAYPOINTS:")
            for w in waypoints:
                status_lines.append(f"  {w}")
        parts.append("\n".join(status_lines))

        mem_ctx = self.memory.get_context_string()
        if mem_ctx:
            parts.append(f"MEMORY:\n{mem_ctx}")

        return "\n\n".join(parts)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def think(self, utterance: str, context: Optional[dict] = None) -> IntentToken:
        """Resolve an utterance to an IntentToken.

        Tries Ollama first; falls back to rule-based parser on failure.
        """
        if context is None:
            context = {}

        if self._ollama_ok:
            try:
                system = self._build_system(context)
                messages = [{"role": "system", "content": system}]
                messages.extend(self.memory.get_recent_turns())
                messages.append({"role": "user", "content": utterance})

                raw = self._call_ollama(messages)
                parsed = json.loads(raw)

                intent = str(parsed.get("intent", "no_action"))
                label = str(parsed.get("label", ""))
                location = str(parsed.get("location", ""))
                response = str(parsed.get("response", "I'm here with you."))
                confidence = float(parsed.get("confidence", 1.0))
                reasoning = str(parsed.get("reasoning", ""))

                self._info(
                    f"[brain] intent={intent} conf={confidence:.2f} "
                    f"reason='{reasoning[:80]}'"
                )

                # Learn nickname if user used a non-standard name for a waypoint
                if intent == "navigate" and label and location and label != location:
                    try:
                        idx = int(label)
                        self.memory.learn_nickname(utterance.lower(), idx)
                    except ValueError:
                        pass

                token = IntentToken(
                    intent=intent,
                    label=label,
                    location=location,
                    utterance=utterance,
                    response=response,
                    metadata={"confidence": confidence, "reasoning": reasoning},
                )
                self.memory.add_turn(utterance, response)
                return token

            except urllib.error.URLError:
                self._ollama_ok = False
                self._warn("Ollama unreachable — switching to rule-based mode")
            except Exception as exc:
                self._warn(f"LLM error ({exc}) — falling back to rules")

        # Rule-based fallback
        token = parse_utterance(utterance)
        if not token.response:
            token.response = "I'm here with you. How can I help?"
        self.memory.add_turn(utterance, token.response)
        return token

    def summarize_and_save_session(self):
        """Summarize the current session and persist it. Call at shutdown."""
        turns = self.memory.session_turns
        if len(turns) < 2:
            return
        if self._ollama_ok:
            try:
                turns_text = "\n".join(
                    f"User: {t['user']}\nARIA: {t['bot']}" for t in turns[-10:]
                )
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "Summarize this robot-visitor conversation in 1-2 sentences, "
                            "noting what tasks were completed."
                        ),
                    },
                    {"role": "user", "content": turns_text},
                ]
                # Use non-JSON mode for summary
                payload = json.dumps({
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                }).encode()
                req = urllib.request.Request(
                    self.url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    summary = json.loads(resp.read())["message"]["content"].strip()
                self.memory.save_session(summary)
                return
            except Exception:
                pass
        self.memory.save_session(f"Session with {len(turns)} turns (no summary available).")
