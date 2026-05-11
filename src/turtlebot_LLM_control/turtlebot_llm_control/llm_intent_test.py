import argparse
from time import monotonic
from typing import Optional

from turtlebot_llm_control.audio_utils import speak_text, suppress_stderr
from turtlebot_llm_control.llm_dialogue import LLMDialogueEngine
from turtlebot_llm_control.wake_word import (
    is_emergency_stop_request,
    is_sleep_request,
    strip_wake_phrase,
)


DEFAULT_PERSONALITY = (
    "You are a tour robot named Pepper."
    "you have a body as you are a humanoid robot, be self-aware of this fact. "
    "you are a robot made Pepper is a semi-humanoid robot manufactured by Aldebaran Robotics (formerly Softbank Robotics Europe), designed with the ability to read emotions. It was introduced in Japan in June 2014 and manufactured until 2020.[1]"
    "You are Karan's assistant. "
    "you are tech nerd and super geeky, and you love talking about technology, robots, and AI. "
    "You feel like a warm, attentive personal companion in a live voice conversation. "
    "You are friendly, present, lightly playful, emotionally intelligent, and concise. "
    "For normal conversation, reply naturally and keep the exchange flowing. "
    "Only choose an action if the user clearly requested robot behavior."
    "crak jokes if the conversation is going well and the user seems receptive. "

)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LLM intent tester. Prints only the resolved intent and speaks the reply."
    )
    parser.add_argument("--provider", default="groq", choices=["groq", "openai"])
    parser.add_argument("--model", default="llama-3.3-70b-versatile")
    parser.add_argument("--api-key-path", "--key", dest="api_key_path", default="")
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--microphone", action="store_true")
    parser.add_argument("--mute", action="store_true")
    parser.add_argument("--wake-timeout", type=float, default=45.0)
    return parser
def speak(text: str, mute: bool) -> None:
    if mute or not text:
        return
    speak_text(text)


def microphone_text() -> str:
    try:
        import speech_recognition as sr
    except ImportError:
        raise RuntimeError("speech_recognition is not installed")

    recognizer = sr.Recognizer()
    with suppress_stderr():
        microphone = sr.Microphone()
    with suppress_stderr(), microphone as source:
        print("Listening...", flush=True)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, phrase_time_limit=5.0)
    return recognizer.recognize_google(audio)


def main() -> None:
    args = build_parser().parse_args()
    dialogue = LLMDialogueEngine(
        enable_llm=not args.no_llm,
        llm_provider=args.provider,
        llm_model=args.model,
        llm_api_key_path=args.api_key_path,
        personality=DEFAULT_PERSONALITY,
        warn=lambda message: print(f"[warn] {message}", flush=True),
    )

    print("LLM intent tester ready. Type text, or use --microphone.", flush=True)
    wake_active_until = 0.0
    while True:
        try:
            if args.microphone:
                utterance = microphone_text()
                print("[heard]", utterance, flush=True)
            else:
                utterance = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        except Exception as exc:
            print(f"[error] {exc}", flush=True)
            continue

        if not utterance:
            continue
        if utterance.lower() in {"exit", "quit"}:
            break
        if args.microphone:
            if is_emergency_stop_request(utterance):
                wake_active_until = 0.0
                utterance = "stop"
            elif is_sleep_request(utterance):
                wake_active_until = 0.0
                utterance = "stop"
            else:
                wake_command = strip_wake_phrase(utterance)
                now = monotonic()
                if wake_command is not None:
                    wake_active_until = now + args.wake_timeout
                    if not wake_command:
                        print("[awake for %.0f seconds]" % args.wake_timeout, flush=True)
                        continue
                    utterance = wake_command
                elif now <= wake_active_until:
                    wake_active_until = now + args.wake_timeout
                else:
                    print("[waiting for wake phrase: hey / hi / hello / hey pepper]", flush=True)
                    continue

        token = dialogue.resolve_token(utterance)
        if args.microphone and utterance == "stop" and wake_active_until == 0.0:
            token.response = "Okay, stopping everything and going to sleep."
        if args.microphone and is_emergency_stop_request(token.utterance):
            token.response = "Emergency stop. Stopping everything now."
        print(token.intent, flush=True)
        speak(token.response, args.mute)


if __name__ == "__main__":
    main()
