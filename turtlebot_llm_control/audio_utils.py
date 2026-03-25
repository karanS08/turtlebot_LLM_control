import os
import shutil
import subprocess
from contextlib import contextmanager
from typing import Iterator, Optional


@contextmanager
def suppress_stderr() -> Iterator[None]:
    try:
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
    except OSError:
        yield
        return

    try:
        saved_stderr_fd = os.dup(2)
    except OSError:
        os.close(devnull_fd)
        yield
        return

    try:
        os.dup2(devnull_fd, 2)
        yield
    finally:
        os.dup2(saved_stderr_fd, 2)
        os.close(saved_stderr_fd)
        os.close(devnull_fd)


def choose_tts_command() -> Optional[list[str]]:
    if shutil.which("spd-say"):
        return ["spd-say", "-w"]
    if shutil.which("espeak"):
        return ["espeak"]
    if shutil.which("say"):
        return ["say"]
    return None


def speak_text(text: str) -> bool:
    if not text:
        return False
    command = choose_tts_command()
    if command is None:
        return False
    try:
        subprocess.run([*command, text], check=False)
        return True
    except OSError:
        return False
