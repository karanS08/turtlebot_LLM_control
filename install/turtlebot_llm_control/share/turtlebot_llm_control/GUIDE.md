# TurtleBot LLM Control Demo Guide

## 1. Purpose

This package is the speech and LLM layer for the social guide robot. It handles:

- speech-to-text input (offline, via faster-whisper)
- conversational LLM layer (Ollama local or Groq/OpenAI cloud)
- wake / sleep / stop voice handling
- navigation intent extraction
- coordinated route recording and playback
- Nav2 goal execution
- voice navigation to named locations

The main showcase is:

- wake Pepper with voice
- ask Pepper to go somewhere, start a tour, or choose stops
- see the intent resolved and published
- hear the spoken reply
- watch the robot move

## 2. Main Files

Core runtime files:

- `launch/sim_pillar_nav_demo.launch.py`
- `launch/bringup.launch.py`
- `launch/intent_only.launch.py`
- `turtlebot_llm_control/sim_initial_pose_node.py`
- `turtlebot_llm_control/speech_to_text_node.py`
- `turtlebot_llm_control/speech_command_node.py`
- `turtlebot_llm_control/speech_response_node.py`
- `turtlebot_llm_control/speech_debug_node.py`
- `turtlebot_llm_control/bt_orchestrator_node.py`
- `turtlebot_llm_control/tour_recording_manager.py`
- `turtlebot_llm_control/tour_teleop_session.py`
- `turtlebot_llm_control/llm_dialogue.py`
- `turtlebot_llm_control/speech_parser.py`
- `turtlebot_llm_control/wake_word.py`
- `turtlebot_llm_control/llm_intent_test.py`
- `speech_locomotion_interface/speech_locomotion_interface/speech_listener.py`
- `speech_locomotion_interface/speech_locomotion_interface/tsp_gui_node.py`

Packaged demo assets:

- `maps/demo/map.yaml`
- `maps/demo/map.pgm`
- `config/demo_nav2/burger.yaml`
- `config/demo_nav2/waffle.yaml`
- `config/demo_nav2/waffle_pi.yaml`
- `rviz/tb3_navigation2.rviz`

## 3. Build

```bash
cd /home/karan/Development/robot_gpt/llm_ws_1
source /opt/ros/humble/setup.bash
pip install faster-whisper
colcon build --packages-select turtlebot_llm_control speech_locomotion_interface
source install/setup.bash
```

Set the robot model before launching:

```bash
export TURTLEBOT3_MODEL=waffle
```

## 4. LLM Requirements

The default provider is **Ollama** running locally — no API key required.

Install Ollama and pull the model:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder
```

Start Ollama if it is not already running as a system service:

```bash
ollama serve
```

Verify it is reachable:

```bash
curl http://localhost:11434/api/tags
```

The `openai` Python package is required as the HTTP client:

```bash
pip install openai
```

To use Groq or OpenAI instead, install the relevant SDK and pass the provider
flags at launch time (see sections 5 and 6).

## 5. Final Demo Launch

Use this for the Gazebo showcase:

```bash
cd /home/karan/Development/robot_gpt/llm_ws_1
source install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot_llm_control sim_pillar_nav_demo.launch.py \
  enable_microphone:=true \
  enable_llm:=true \
  llm_provider:=ollama \
  llm_model:=qwen2.5-coder:latest \
  mute:=false \
  enable_speech_debug:=true
```

What this launch starts:

- TurtleBot3 Gazebo world
- Nav2 bringup
- RViz
- speech-to-text node (faster-whisper)
- speech command node
- speech response speaker node
- speech debug node
- behavior-tree orchestrator
- tour recording manager
- follow node
- initial pose publisher for the simulated robot

Optional direct locomotion mode:

- pass `enable_direct_locomotion_interface:=true` to also launch the
  `speech_locomotion_interface` package

Recording flow:

- saying `start recording` enters recording mode
- use `w`, `a`, `s`, `d` to move the robot during the recording session
- press `r` then `Enter` in the teleop terminal to publish the current route label
- press `esc` to stop teleop and return to autonomy

## 6. Intent-Only Launch

Use this when the robot workspace (`turtlebot_social_guide`) owns navigation, touring, and docking. This launch provides:

- `speech_to_text_node` (faster-whisper, offline)
- `speech_command_node` (LLM intent resolver)
- optional `speech_debug_node`
- optional `speech_response_node`

It publishes resolved intent JSON to `/speech/intent`.

```bash
cd /home/karan/Development/robot_gpt/llm_ws_1
source /opt/ros/humble/setup.bash
source /home/karan/Development/robot_gpt/turtlebot_social_guide/install/setup.bash
source install/setup.bash
ros2 launch turtlebot_llm_control intent_only.launch.py \
  enable_microphone:=true \
  enable_llm:=true \
  llm_provider:=ollama \
  llm_model:=qwen2.5-coder:latest \
  intent_topic:=/speech/intent \
  enable_speech_debug:=true \
  enable_speech_response:=true \
  enable_tour_teleop_trigger:=true
```

To test without the microphone:

```bash
ros2 launch turtlebot_llm_control intent_only.launch.py \
  enable_microphone:=false \
  intent_topic:=/speech/intent
```

Then inject text:

```bash
ros2 topic pub --once /speech/mock_text std_msgs/msg/String "{data: 'hey pepper start the tour'}"
```

Useful echo targets:

```bash
ros2 topic echo /speech/intent
ros2 topic echo /speech/response
ros2 topic echo /speech_to_text/status
ros2 topic echo /speech/debug
```

## 7. Standalone Tester

```bash
cd /home/karan/Development/robot_gpt/llm_ws_1
source install/setup.bash
ros2 run turtlebot_llm_control llm_intent_test \
  --provider ollama \
  --model qwen2.5-coder:latest \
  --microphone
```

Useful flags:

- `--mute`
- `--no-llm`
- `--wake-timeout 45.0`
- `--list-microphones`
- `--mic-device 0`
- `--energy-threshold 150`

If the tester never hears you, first list available microphones:

```bash
ros2 run turtlebot_llm_control llm_intent_test --list-microphones
```

Then run with the matching device index:

```bash
ros2 run turtlebot_llm_control llm_intent_test \
  --provider ollama \
  --model qwen2.5-coder:latest \
  --microphone \
  --mic-device 0
```

## 8. Speech-to-Text Configuration

The STT node uses **faster-whisper** — a local, offline Whisper implementation. No internet connection is required.

### Why faster-whisper

- Runs fully offline (no Google API, no rate limits)
- Built-in Silero VAD (`vad_filter=True`) — accurate voice activity detection, no word clipping from energy thresholds
- `initial_prompt` biases recognition towards robot vocabulary (`stop`, `navigate`, `pillar`, `waypoint`, etc.)
- Base model is ~145 MB and fast enough for real-time on CPU

### Model download

On first run the node downloads the model (~145 MB) from Hugging Face into `~/.cache/huggingface/`. Subsequent starts load from cache.

### ROS2 parameters

| Parameter | Default | Meaning |
| --- | --- | --- |
| `enable_microphone` | `false` | Enable live microphone input |
| `mic_device_index` | `-1` | Microphone device index (`-1` = system default) |
| `phrase_time_limit` | `5.0` | Max seconds of audio captured per phrase |
| `energy_threshold` | `300` | Minimum audio energy to start capture (used before VAD) |
| `dynamic_energy_threshold` | `true` | Automatically adjust energy threshold |
| `calibrate_ambient_noise` | `true` | Calibrate for background noise on startup |
| `require_wake_word` | `true` | Ignore speech until a wake phrase is heard |
| `wake_command_window_seconds` | `45.0` | Seconds Pepper stays awake after wake phrase |
| `tts_cooldown_seconds` | `1.0` | Seconds to pause STT after TTS finishes |
| `whisper_model_size` | `"base"` | Whisper model: `tiny`, `base`, `small`, `medium` |
| `whisper_device` | `"cpu"` | Compute device: `cpu` or `cuda` |

To use a more accurate model (slower to load, better recognition):

```bash
ros2 launch turtlebot_llm_control intent_only.launch.py \
  enable_microphone:=true \
  whisper_model_size:=small
```

If `faster-whisper` is not installed the node falls back to Google STT automatically and logs a warning.

## 9. Voice Behavior

Wake phrases:

- `hey pepper`
- `hi pepper`
- `hello pepper`
- `pepper`

After wake-up:

- Pepper stays awake for 45 seconds of inactivity
- each new utterance resets the timer
- silence long enough sends Pepper back to sleep

Sleep commands:

- `good night pepper`
- `sleep pepper`
- `pepper sleep`

Emergency stop commands (bypass wake gate):

- `stop`
- `stop stop`
- `stop now`
- `emergency stop`

## 10. Intent Reference

The speech parser handles these intents directly (no LLM needed):

| Intent | Example phrases |
| --- | --- |
| `navigate` | "go to pillar 3", "take me to the lab", "lead me to waypoint 2" |
| `start_tour` | "start tour", "full tour", "show me everything", "tour please" |
| `tsp` | "short tour", "show me around", "let me choose", "my own tour", "pick some stops" |
| `dock` | "go home", "go charge", "recharge", "return to base", "go plug in" |
| `stop` | "stop", "halt", "abort", "never mind", "hold on", "that's enough" |
| `stop_navigation` | "stop navigation", "cancel navigation" |
| `pause` | "pause" |
| `resume` | "resume" |
| `explain` | "tell me about", "what is this room", "describe", "what can I see here" |
| `is_alive` | "hey pepper", "are you awake", "are you there" |
| `manual_override_on` | "manual override", "take over", "enable teleop" |
| `manual_override_off` | "return to autonomous", "disable manual override" |

Unrecognized commands fall through to the LLM which also handles casual conversation (`no_action`).

## 11. Demo Commands

Recommended spoken sequence:

```text
hey pepper
go to pillar 1
```

Other supported forms:

- `go to pillar 5`
- `go to pillar five`
- `take me to pillar 3`
- `take me to pillow one`
- `pepper go to pillar 9`
- `start the tour`
- `show me around` (opens TSP GUI for custom stop selection)
- `go home` (docking)

If the pillar number is missing, Pepper asks for clarification instead of creating a bad goal.

## 12. TSP GUI

When a `tsp` intent is received the system opens a waypoint selection window.

- the GUI is a persistent ROS2 node started by the launch file — it does not re-launch each time
- it is triggered to show via the `/tsp_gui/show` topic
- click waypoints in the order you want to visit them — numbers show the visit sequence
- orange lines connect your chosen stops
- press **Start** to send the tour and hide the window
- press **Clear** to reset the selection

To trigger it manually for testing:

```bash
ros2 topic pub --once /tsp_gui/show std_msgs/msg/String "{data: show}"
```

## 13. Speech And Debug Topics

Main topics:

- `/speech/text` — raw STT transcript
- `/speech/intent` — resolved intent JSON
- `/speech/response` — robot spoken reply text
- `/speech/debug` — combined debug stream
- `/speech_to_text/status` — STT node status (model load, recognition events)
- `/tsp_gui/show` — trigger TSP GUI to appear

For clean speech debugging:

```bash
ros2 topic echo /speech/debug
```

This is the best topic to watch during the demo — it shows STT status, recognized text, resolved intent, and spoken response in one stream.

Watch STT recognition quality:

```bash
ros2 topic echo /speech_to_text/status
```

## 14. Notes On TTS

The package uses local desktop TTS tools for audio playback.

Supported commands (checked in order):

- `spd-say`
- `espeak`
- `say`

If Pepper is not speaking:

```bash
which spd-say
which espeak
```

## 15. Known Runtime Noise

You may still see Nav2 / AMCL messages like:

- `Message Filter dropping message`
- TF cache timestamp warnings

These usually happen during startup while Gazebo, TF, localization, and Nav2 are settling.

What matters for the demo:

- `/speech/debug` shows the right text and intent
- Pepper speaks a response
- the robot accepts the navigation goal and moves

## 16. Quick Checklist

Before the demo:

1. `pip install faster-whisper` (one-time)
2. `colcon build --packages-select turtlebot_llm_control speech_locomotion_interface`
3. `source install/setup.bash`
4. `export TURTLEBOT3_MODEL=waffle`
5. confirm Ollama is running: `curl http://localhost:11434/api/tags`
6. launch `sim_pillar_nav_demo.launch.py` (Gazebo) or `intent_only.launch.py` (social guide mode)
7. watch `ros2 topic echo /speech_to_text/status` — look for `Loaded faster-whisper 'base' model`
8. watch `ros2 topic echo /speech/debug` during the demo

## 17. One-Line Demo Reminder

```text
hey pepper → go to pillar one → Pepper answers → intent resolves → robot navigates
```
