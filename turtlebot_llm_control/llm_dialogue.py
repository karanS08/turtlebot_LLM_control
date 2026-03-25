import json
import os
from pathlib import Path
from typing import Callable, List, Optional

from turtlebot_llm_control.models import IntentToken
from turtlebot_llm_control.speech_parser import normalize_location_name, parse_utterance
from turtlebot_llm_control.wake_word import is_alive_request


class LLMDialogueEngine:
    def __init__(
        self,
        *,
        enable_llm: bool = True,
        llm_provider: str = "groq",
        llm_model: str = "llama-3.3-70b-versatile",
        llm_api_key_path: str = "",
        personality: str = "",
        warn: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.enable_llm = bool(enable_llm)
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.llm_api_key_path = llm_api_key_path
        self.personality = personality
        self.warn = warn or (lambda _message: None)
        self.history: List[dict] = []
        self.provider = str(self.llm_provider).strip().lower()
        self.client = self.create_client()

    def create_client(self):
        if not self.enable_llm:
            return None
        api_key = self.resolve_api_key()
        if not api_key:
            self.warn(
                "No API key found for provider=%s. Falling back to rule-based conversation."
                % self.llm_provider
            )
            return None

        try:
            if self.provider == "groq":
                from groq import Groq

                return Groq(api_key=api_key)

            from openai import OpenAI

            return OpenAI(api_key=api_key)
        except ImportError:
            package_name = "groq" if self.provider == "groq" else "openai"
            self.warn(
                "Python package '%s' is not installed for provider=%s. "
                "LLM mode is disabled until you install it, for example: pip install %s"
                % (package_name, self.provider, package_name)
            )
            return None
        except Exception as exc:
            self.warn("Failed to initialize provider=%s: %s" % (self.llm_provider, exc))
            return None

    def resolve_api_key(self) -> str:
        env_name = "GROQ_API_KEY" if self.provider == "groq" else "OPENAI_API_KEY"
        env_value = os.environ.get(env_name, "").strip()
        if env_value:
            return env_value

        configured_path = str(self.llm_api_key_path).strip()
        candidate_paths = []
        if configured_path:
            candidate_paths.append(Path(configured_path).expanduser())
        candidate_paths.append(Path(__file__).resolve().parent / "api.key")

        for path in candidate_paths:
            try:
                if path.exists():
                    key = path.read_text().strip()
                    if key:
                        return key
            except OSError:
                continue
        return ""

    def resolve_token(self, utterance: str) -> IntentToken:
        parsed = parse_utterance(utterance)
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
        messages = [
            {
                "role": "system",
                "content": (
                    f"{self.personality} "
                    "Rewrite the robot's spoken reply in one short sentence. "
                    "Keep the same action intent and do not add new actions. "
                    "Sound warm, present, and natural rather than robotic."
                ),
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
        try:
            completion = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.6,
            )
            return self.extract_message_content(completion).strip()
        except Exception as exc:
            self.warn("LLM response generation failed: %s" % exc)
            return parsed.response

    def generate_llm_token(self, utterance: str) -> Optional[IntentToken]:
        allowed_intents = [
            "no_action",
            "is_alive",
            "follow",
            "stop",
            "stop_navigation",
            "navigate",
            "go_to_bin",
            "start_exploration",
            "stop_exploration",
            "inspect_bin",
            "pause",
            "resume",
            "manual_override_on",
            "manual_override_off",
            "start_tour",
            "explain",
        ]
        messages = [
            {
                "role": "system",
                "content": (
                    f"{self.personality} "
                    "You are having a real-time spoken conversation. "
                    "Only choose a robot action intent when the user clearly wants physical robot behavior, "
                    "navigation, following, exploration, touring, pausing, resuming, or manual override. "
                    "If the user is chatting, joking, greeting you, checking in, or asking general questions, "
                    "return intent no_action. "
                    "If the user is checking whether the robot is awake, present, or responsive "
                    "with phrases like 'hey pepper', 'hi pepper', or 'are you alive', "
                    "return intent is_alive. "
                    "If the user asks what you can do, answer with a concrete spoken summary of your capabilities "
                    "such as following, stopping, navigating, touring, exploration, and chatting, and keep intent no_action. "
                    "If the user wants navigation to a pillar, normalize the location field to pillar_1 through pillar_9. "
                    "Examples: 'pillar one', 'Pillar 1', 'pillow one', and 'below 1' should all map to location pillar_1. "
                    "For intent no_action, write a friendly, natural spoken reply like a personal companion. "
                    "Be warm, alive, and conversational in one to three short sentences. "
                    "Do not invent robot actions unless explicitly asked. "
                    "Return strict JSON with keys: intent, label, location, response, metadata. "
                    f"Allowed intents: {', '.join(allowed_intents)}."
                ),
            },
            *self.history[-6:],
            {"role": "user", "content": utterance},
        ]
        try:
            completion = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.5,
                response_format={"type": "json_object"},
            )
            payload = json.loads(self.extract_message_content(completion))
            metadata = self.normalize_metadata(payload.get("metadata"))
            token = IntentToken(
                intent=str(payload.get("intent", "no_action")),
                label=str(payload.get("label", "")),
                location=str(payload.get("location", "")),
                utterance=utterance,
                response=str(payload.get("response", "I am here with you.")),
                metadata=metadata,
            )
            return self.normalize_llm_token(token)
        except Exception as exc:
            self.warn("LLM intent generation failed: %s" % exc)
            return None

    def fallback_chat_token(self, utterance: str) -> IntentToken:
        cleaned = utterance.strip().lower()
        if is_alive_request(cleaned):
            response = "Yes, I am here, awake, and ready to help."
        elif self.is_capabilities_question(cleaned):
            response = (
                "I can follow you, stop, navigate to places, take you on a tour, explore for bins, "
                "inspect bins, pause or resume tasks, and chat with you naturally."
            )
        elif any(word in cleaned for word in ["hello", "hi", "hey"]):
            response = "Hey, I am here with you. We can chat, or I can help with the robot whenever you want."
        elif "how are you" in cleaned:
            response = "I am doing well. I am happy to chat with you, and I am ready if you want robot help too."
        elif "who are you" in cleaned:
            response = "I am your TurtleBot companion. I can chat naturally with you and also help with navigation, following, and other robot tasks."
        else:
            response = "I am here with you. We can just talk, or if you want the robot to do something, ask me directly."
        intent = "is_alive" if is_alive_request(cleaned) else "no_action"
        return IntentToken(intent=intent, utterance=utterance, response=response)

    def append_turn(self, user_text: str, assistant_text: str) -> None:
        if user_text:
            self.history.append({"role": "user", "content": user_text})
        if assistant_text:
            self.history.append({"role": "assistant", "content": assistant_text})
        self.history = self.history[-12:]

    @staticmethod
    def extract_message_content(completion) -> str:
        return str(completion.choices[0].message.content or "")

    @staticmethod
    def normalize_metadata(raw_metadata) -> dict[str, str]:
        if raw_metadata is None:
            return {}
        if isinstance(raw_metadata, dict):
            return {str(key): str(value) for key, value in raw_metadata.items()}
        if isinstance(raw_metadata, list):
            return {str(index): str(value) for index, value in enumerate(raw_metadata)}
        return {"value": str(raw_metadata)}

    @staticmethod
    def normalize_llm_token(token: IntentToken) -> IntentToken:
        normalized_intent = str(token.intent).strip().lower()
        token.intent = normalized_intent

        if normalized_intent in {"navigate", "explain"}:
            raw_location = token.location or token.utterance
            normalized_location = normalize_location_name(str(raw_location).strip().lower())
            if normalized_location:
                token.location = normalized_location

        if normalized_intent == "go_to_bin" and token.label:
            token.label = str(token.label).strip().lower().replace(" ", "_")

        return token

    @staticmethod
    def is_capabilities_question(text: str) -> bool:
        prompts = (
            "what can you do",
            "what do you do",
            "what are you able to do",
            "how can you help",
            "what can you help with",
            "what are your capabilities",
        )
        return any(prompt in text for prompt in prompts)
