import json
import time
from pathlib import Path


class MemoryManager:
    """Three-layer persistent memory for the robot brain.

    Working  — in-process list of last 20 conversation turns (cleared each session).
    Episodic — JSON file: session summaries (last 10) and learned waypoint nicknames.
    Semantic — same JSON file: facts learned about visitors / environment.
    """

    _DEFAULT_DATA = {"sessions": [], "facts": [], "waypoint_nicknames": {}}

    def __init__(self, memory_file: str = "~/.ros/robot_memory.json"):
        self.file_path = Path(memory_file).expanduser()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()
        self.session_turns: list[dict] = []

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        if self.file_path.exists():
            try:
                return json.loads(self.file_path.read_text())
            except Exception:
                pass
        return dict(self._DEFAULT_DATA)

    def _save(self):
        try:
            self.file_path.write_text(json.dumps(self.data, indent=2))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Working memory (current session)
    # ------------------------------------------------------------------

    def add_turn(self, user_text: str, bot_response: str):
        self.session_turns.append({"user": user_text, "bot": bot_response})
        if len(self.session_turns) > 20:
            self.session_turns = self.session_turns[-20:]

    def get_recent_turns(self) -> list[dict]:
        """Return last 20 turns in Ollama messages format."""
        messages = []
        for turn in self.session_turns[-20:]:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["bot"]})
        return messages

    # ------------------------------------------------------------------
    # Episodic / semantic memory (persistent)
    # ------------------------------------------------------------------

    def learn_nickname(self, nickname: str, waypoint_index: int):
        """Store a user-provided nickname → waypoint index mapping."""
        self.data.setdefault("waypoint_nicknames", {})[nickname.lower()] = waypoint_index
        self._save()

    def add_fact(self, fact: str):
        """Store a semantic fact learned about visitors or environment."""
        facts = self.data.setdefault("facts", [])
        facts.append(fact)
        self.data["facts"] = facts[-20:]
        self._save()

    def save_session(self, summary: str):
        """Append a session summary (called at shutdown)."""
        sessions = self.data.setdefault("sessions", [])
        sessions.append({
            "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "summary": summary,
        })
        self.data["sessions"] = sessions[-10:]
        self._save()

    def get_context_string(self) -> str:
        """Compact text block injected into every LLM system prompt."""
        parts = []

        last_sessions = self.data.get("sessions", [])[-3:]
        if last_sessions:
            parts.append("Previous sessions:")
            for s in last_sessions:
                parts.append(f"  {s.get('date', '')[:10]}: {s.get('summary', '')}")

        nicknames = self.data.get("waypoint_nicknames", {})
        if nicknames:
            nick_str = ", ".join(f'"{k}"→wp{v}' for k, v in list(nicknames.items())[:8])
            parts.append(f"Learned nicknames: {nick_str}")

        facts = self.data.get("facts", [])
        if facts:
            parts.append("Known facts: " + "; ".join(facts[-5:]))

        return "\n".join(parts)
