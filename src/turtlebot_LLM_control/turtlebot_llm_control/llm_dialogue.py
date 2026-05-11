"""LLM dialogue engine backed by a local Ollama server.

All inference is fully offline — no cloud API keys required.
The default model is ``qwen2.5:7b`` which runs comfortably on a laptop GPU
or CPU.  Change ``llm_model`` to any model you have pulled in Ollama.

Ollama must be running before the node starts:

    ollama serve          # starts the server on localhost:11434
    ollama pull qwen2.5:7b
"""

from __future__ import annotations

import json
from typing import Callable, List, Optional

from turtlebot_llm_control.knowledge_store import KnowledgeStore
from turtlebot_llm_control.models import IntentToken
from turtlebot_llm_control.speech_parser import normalize_location_name, parse_utterance
from turtlebot_llm_control.wake_word import is_alive_request

_OLLAMA_IMPORT_ERROR = (
    "Python package 'ollama' is not installed. "
    "Run:  pip install ollama\n"
    "Falling back to rule-based conversation."
)


class LLMDialogueEngine:
    def __init__(
        self,
        *,
        enable_llm: bool = True,
        llm_model: str = "qwen2.5:7b",
        ollama_host: str = "http://localhost:11434",
        knowledge_db_path: str = "",
        personality: str = "",
        warn: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.enable_llm = bool(enable_llm)
        self.llm_model = llm_model
        self.ollama_host = ollama_host.rstrip("/")
        self.personality = personality
        self.warn = warn or (lambda _: None)
        self.history: List[dict] = []
        self.client = self._create_client()
        self.knowledge_store = KnowledgeStore(str(knowledge_db_path))

    # ------------------------------------------------------------------
    # Ollama client
    # ------------------------------------------------------------------

    def _create_client(self):
        if not self.enable_llm:
            return None
        try:
            import ollama  # noqa: F401 — just verify it is importable

            # Return a thin wrapper that holds the host so all call sites
            # can use a uniform interface.
            return _OllamaClient(
                model=self.llm_model,
                host=self.ollama_host,
                warn=self.warn,
            )
        except ImportError:
            self.warn(_OLLAMA_IMPORT_ERROR)
            return None
        except Exception as exc:
            self.warn("Failed to initialise Ollama client: %s" % exc)
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve_token(self, utterance: str) -> IntentToken:
        parsed = parse_utterance(utterance)
        knowledge_response = self.generate_knowledge_response(utterance)

        if knowledge_response is not None and (
            parsed.intent in {"unknown", "no_action", "explain"}
            or self.is_knowledge_question(utterance)
        ):
            parsed.intent = "explain"
            parsed.response = knowledge_response
            if not parsed.location:
                parsed.location = self.knowledge_location_hint(utterance)
            self.append_turn(utterance, parsed.response)
            return parsed

        if parsed.intent != "unknown":
            if self.client is not None:
                response = self.generate_personalized_response(parsed)
                if response:
                    parsed.response = response
            self.append_turn(utterance, parsed.response)
            return parsed

        if self.client is not None:
            llm_token = self.generate_llm_token(utterance)
            if llm_token is not None:
                self.append_turn(utterance, llm_token.response)
                return llm_token

        fallback = self.fallback_chat_token(utterance)
        self.append_turn(utterance, fallback.response)
        return fallback

    def generate_personalized_response(self, parsed: IntentToken) -> str:
        if self.client is None:
            return parsed.response
        messages = [
            {
                "role": "system",
                "content": (
                    "%s "
                    "Rewrite the robot's spoken reply in one short sentence. "
                    "Keep the same action intent and do not add new actions. "
                    "Sound warm, present, and natural rather than robotic."
                ) % self.personality,
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "utterance": parsed.utterance,
                        "intent": parsed.intent,
                        "current_response": parsed.response,
                    }
                ),
            },
        ]
        return self.client.chat(messages, temperature=0.6) or parsed.response

    def generate_knowledge_response(self, utterance: str) -> Optional[str]:
        context = self.knowledge_store.build_context(utterance, limit=3)
        if not context:
            return None

        if self.client is None:
            summary = self.knowledge_store.summarize_hits(utterance, limit=3)
            return summary or context

        messages = [
            {
                "role": "system",
                "content": (
                    "%s "
                    "You answer questions about museum or tour content, places, artifacts, and wiki notes. "
                    "Use only the provided context. If the context does not contain the answer, say so briefly. "
                    "Keep the answer short, direct, and helpful. "
                    "Do not invent facts."
                ) % self.personality,
            },
            {
                "role": "user",
                "content": json.dumps({"question": utterance, "context": context}),
            },
        ]
        result = self.client.chat(messages, temperature=0.2)
        return result or self.knowledge_store.summarize_hits(utterance, limit=3) or context

    def generate_llm_token(self, utterance: str) -> Optional[IntentToken]:
        allowed_intents = [
            "no_action", "is_alive", "stop", "stop_navigation", "navigate",
            "pause", "resume", "manual_override_on", "manual_override_off",
            "start_tour", "start_recording", "stop_recording", "save_route",
            "replay_route", "explain",
        ]
        messages = [
            {
                "role": "system",
                "content": (
                    "%s "
                    "You are having a real-time spoken conversation. "
                    "Only choose a robot action intent when the user clearly wants physical robot behavior, "
                    "navigation, touring, recording, pausing, resuming, or manual override. "
                    "If the user is chatting, joking, greeting you, or asking general questions, "
                    "return intent no_action. "
                    "If the user is checking whether the robot is awake, return intent is_alive. "
                    "Return strict JSON with keys: intent, label, location, response, metadata. "
                    "Allowed intents: %s."
                ) % (self.personality, ", ".join(allowed_intents)),
            },
            *self.history[-6:],
            {"role": "user", "content": utterance},
        ]
        raw = self.client.chat(messages, temperature=0.5, json_mode=True)
        if raw is None:
            return None
        try:
            payload = json.loads(raw)
            token = IntentToken(
                intent=str(payload.get("intent", "no_action")),
                label=str(payload.get("label", "")),
                location=str(payload.get("location", "")),
                utterance=utterance,
                response=str(payload.get("response", "I am here with you.")),
                metadata=self._normalize_metadata(payload.get("metadata")),
            )
            return self._normalize_llm_token(token)
        except Exception as exc:
            self.warn("LLM intent parse error: %s  raw=%r" % (exc, raw))
            return None

    # ------------------------------------------------------------------
    # Fallback (no LLM)
    # ------------------------------------------------------------------

    def fallback_chat_token(self, utterance: str) -> IntentToken:
        cleaned = utterance.strip().lower()
        if is_alive_request(cleaned):
            response = "Yes, I am here, awake, and ready to help."
            intent = "is_alive"
        elif self.is_capabilities_question(cleaned):
            response = (
                "I can stop, navigate to places, take you on a tour, record routes, "
                "pause or resume tasks, and chat with you naturally."
            )
            intent = "no_action"
        elif any(w in cleaned for w in ["hello", "hi", "hey"]):
            response = "Hey, I am here. We can chat, or I can help with navigation whenever you want."
            intent = "no_action"
        elif "how are you" in cleaned:
            response = "I am doing well. Ready to help whenever you need me."
            intent = "no_action"
        elif "who are you" in cleaned:
            response = (
                "I am your TurtleBot companion. I can navigate, run tours, and "
                "answer questions about what we see."
            )
            intent = "no_action"
        else:
            response = "I am here with you. Just ask if you want the robot to do something."
            intent = "no_action"
        return IntentToken(intent=intent, utterance=utterance, response=response)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def append_turn(self, user_text: str, assistant_text: str) -> None:
        if user_text:
            self.history.append({"role": "user", "content": user_text})
        if assistant_text:
            self.history.append({"role": "assistant", "content": assistant_text})
        self.history = self.history[-12:]

    @staticmethod
    def _normalize_metadata(raw) -> dict[str, str]:
        if raw is None:
            return {}
        if isinstance(raw, dict):
            return {str(k): str(v) for k, v in raw.items()}
        if isinstance(raw, list):
            return {str(i): str(v) for i, v in enumerate(raw)}
        return {"value": str(raw)}

    @staticmethod
    def _normalize_llm_token(token: IntentToken) -> IntentToken:
        token.intent = str(token.intent).strip().lower()
        if token.intent in {"navigate", "explain"}:
            raw = token.location or token.utterance
            normalized = normalize_location_name(str(raw).strip().lower())
            if normalized:
                token.location = normalized
        return token

    @staticmethod
    def is_knowledge_question(text: str) -> bool:
        cleaned = text.strip().lower()
        if not cleaned:
            return False
        # These are NOT knowledge questions — they are conversation starters.
        for skip in (
            "what can you do", "what do you do", "how can you help",
            "who are you", "what are you", "how are you",
            "hello", "hi ", " hey",
        ):
            if skip in cleaned:
                return False
        prompts = (
            "tell me about", "explain", "describe",
            "what is", "what are", "who is", "who are",
            "where is", "where are",
            "what do you know about", "what can you tell me about",
            "give me details about", "why is", "how does", "how do",
        )
        return cleaned.endswith("?") or any(
            cleaned.startswith(p) or p in cleaned for p in prompts
        )

    def knowledge_location_hint(self, text: str) -> str:
        return normalize_location_name(text.strip().lower())

    @staticmethod
    def is_capabilities_question(text: str) -> bool:
        prompts = (
            "what can you do", "what do you do", "what are you able to do",
            "how can you help", "what can you help with", "what are your capabilities",
        )
        return any(p in text for p in prompts)


# ---------------------------------------------------------------------------
# Internal Ollama wrapper
# ---------------------------------------------------------------------------

class _OllamaClient:
    """Thin wrapper around the ``ollama`` Python package.

    Presents a single ``.chat()`` method so the rest of the code has no
    direct dependency on the ollama package's API shape.
    """

    def __init__(self, *, model: str, host: str, warn: Callable[[str], None]) -> None:
        import ollama

        self._ollama = ollama
        self._model = model
        self._host = host
        self._warn = warn
        # Create a client scoped to the configured host.
        self._client = ollama.Client(host=host)

    def chat(
        self,
        messages: List[dict],
        temperature: float = 0.5,
        json_mode: bool = False,
    ) -> Optional[str]:
        kwargs: dict = {
            "model": self._model,
            "messages": messages,
            "options": {"temperature": temperature},
        }
        if json_mode:
            kwargs["format"] = "json"
        try:
            response = self._client.chat(**kwargs)
            return str(response.message.content or "").strip()
        except Exception as exc:
            self._warn("Ollama chat error: %s" % exc)
            return None
