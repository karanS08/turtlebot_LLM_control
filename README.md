# TurtleBot LLM Control

Speech and LLM layer for the Social Guide Robot. Converts spoken language into ROS2 intents and robot actions, using offline speech recognition, a local LLM, and a PyQt5 waypoint-selector GUI.

Developed by **Karan Sharma** as part of the **Social Tour Guide Robot** project at the University of Technology Sydney — Robotics Studio 2 (41069).

---

## What It Does

- Listens for a wake phrase, then transcribes speech with **faster-whisper** (fully offline)
- Resolves utterances into structured intents via rule-based parser + **Ollama** LLM fallback
- Publishes robot commands to `/speech/intent` for the navigation layer to consume
- Speaks replies back through the local TTS engine
- Opens a **TSP waypoint-selector GUI** when the user asks for a custom tour
- Publishes a live **emotion state** (`thinking / speaking / explaining / greeting / idle`) on `/emotions`

---

## Architecture

```
Microphone
    │
    ▼
speech_to_text_node      ──► /speech/text
    │
    ▼
speech_command_node      ──► /speech/intent   (navigate, start_tour, dock, stop, …)
    │                    ──► /speech/response  (text to speak aloud)
    │                    ──► /tsp_gui/show     (triggers waypoint GUI)
    │
    ├── speech_response_node   (TTS: spd-say / espeak)
    ├── speech_debug_node      ──► /speech/debug
    ├── tour_intent_bridge_node (start/stop recording)
    ├── tsp_gui_node           ──► /tsp_command  (TspCommand: list of waypoint indices)
    └── emotion_node           ──► /emotions     (thinking / speaking / explaining / greeting / idle)
```

---

## Nodes

| Executable | Role |
|---|---|
| `speech_to_text_node` | faster-whisper STT; publishes raw transcript to `/speech/text` |
| `speech_command_node` | Resolves text → intent via parser + Ollama LLM |
| `speech_response_node` | Reads `/speech/response` and speaks it via system TTS |
| `speech_debug_node` | Aggregates all speech topics into `/speech/debug` |
| `tour_intent_bridge_node` | Handles `start_recording` / `stop_recording` intents |
| `tsp_gui` | PyQt5 GUI — select waypoints in order, publishes `TspCommand` to `/tsp_command` |
| `emotion_node` | Classifies conversation into 5 emotions and publishes to `/emotions` |
| `bt_orchestrator_node` | Nav2 goal orchestration |
| `tour_recording_manager` | Records and saves robot routes |
| `tour_teleop_session` | Teleoperation during a recording session |
| `follow_me_node` | Person-following behaviour |
| `sim_initial_pose_node` | Sets initial pose in Gazebo |
| `llm_intent_test` | Standalone command-line tester (no ROS nav stack needed) |

---

## Topics

| Topic | Type | Direction | Description |
|---|---|---|---|
| `/speech/text` | `std_msgs/String` | pub | Raw STT transcript |
| `/speech/mock_text` | `std_msgs/String` | sub | Inject text without microphone |
| `/speech/intent` | `std_msgs/String` | pub | Resolved intent JSON |
| `/speech/response` | `std_msgs/String` | pub | Robot reply text |
| `/speech/debug` | `std_msgs/String` | pub | Aggregated debug stream |
| `/speech_to_text/status` | `std_msgs/String` | pub | STT node status events |
| `/speech/tts_active` | `std_msgs/Bool` | sub | Mutes STT while robot is speaking |
| `/tsp_gui/show` | `std_msgs/String` | sub | Triggers TSP GUI to open |
| `/tsp_command` | `TspCommand` | pub | Ordered list of waypoint indices |
| `/emotions` | `std_msgs/String` | pub | Current robot emotion state |

---

## Setup

**Dependencies**

```bash
pip install faster-whisper openai
```

**Ollama** (local LLM, no API key required)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder
ollama serve
```

**Build**

```bash
cd /home/karan/Development/robot_gpt/llm_ws_1
source /opt/ros/humble/setup.bash
colcon build --packages-select turtlebot_llm_control
source install/setup.bash
```

---

## Launch

### Intent-only mode (used with `turtlebot_social_guide` for navigation)

```bash
source /opt/ros/humble/setup.bash
source /home/karan/Development/robot_gpt/turtlebot_social_guide/install/setup.bash
source install/setup.bash

ros2 launch turtlebot_llm_control intent_only.launch.py \
  enable_microphone:=true \
  llm_provider:=ollama \
  llm_model:=qwen2.5-coder:latest
```

Key launch arguments:

| Argument | Default | Description |
|---|---|---|
| `enable_microphone` | `true` | Live mic input via faster-whisper |
| `mic_device_index` | `-1` | Mic device (`-1` = system default) |
| `energy_threshold` | `150` | Mic capture sensitivity |
| `phrase_time_limit` | `5.0` | Max seconds per phrase |
| `require_wake_word` | `true` | Ignore speech until wake phrase heard |
| `wake_command_window_seconds` | `45.0` | Seconds Pepper stays awake after wake |
| `llm_provider` | `ollama` | `ollama`, `openai`, or `groq` |
| `llm_model` | `qwen2.5-coder:latest` | Model name for the chosen provider |
| `mute` | `false` | Disable TTS speaker output |
| `enable_tsp_gui` | `true` | Launch TSP waypoint selector GUI |
| `enable_emotion` | `true` | Launch emotion publisher node |

### Gazebo simulation demo

```bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot_llm_control sim_pillar_nav_demo.launch.py \
  enable_microphone:=true \
  llm_provider:=ollama \
  llm_model:=qwen2.5-coder:latest
```

---

## Testing Without a Microphone

```bash
ros2 launch turtlebot_llm_control intent_only.launch.py enable_microphone:=false
```

Inject speech in another terminal:

```bash
ros2 topic pub --once /speech/mock_text std_msgs/msg/String "{data: 'hey pepper start the tour'}"
```

Monitor output:

```bash
ros2 topic echo /speech/debug       # combined stream — best for live debugging
ros2 topic echo /speech/intent      # resolved intent JSON
ros2 topic echo /speech/response    # robot reply text
ros2 topic echo /emotions           # emotion state
```

Trigger the TSP GUI manually:

```bash
ros2 topic pub --once /tsp_gui/show std_msgs/msg/String "{data: show}"
```

Echo `/tsp_command` to verify waypoint selection:

```bash
ros2 topic echo /tsp_command
```

---

## Voice Commands

Wake phrases:

```
hey pepper  |  hi pepper  |  hello pepper  |  pepper
```

Sleep / stop listening:

```
good night pepper  |  sleep pepper  |  pepper sleep
```

Emergency stop (bypasses wake gate):

```
stop  |  stop stop  |  stop now  |  emergency stop
```

### Intent Reference

| Intent | Example phrases |
|---|---|
| `navigate` | "go to pillar 3", "take me to the lab", "lead me to waypoint 2" |
| `start_tour` | "start tour", "full tour", "show me everything", "tour please" |
| `tsp` | "short tour", "show me around", "let me choose some stops", "pick stops" |
| `dock` | "go home", "go charge", "recharge", "return to base" |
| `stop` | "stop", "halt", "abort", "never mind", "that's enough" |
| `stop_navigation` | "stop navigation", "cancel navigation" |
| `pause` | "pause" |
| `resume` | "resume" |
| `explain` | "tell me about this", "what is this room", "describe this area" |
| `is_alive` | "hey pepper", "are you awake", "are you there" |
| `start_recording` | "start recording" |
| `stop_recording` | "stop recording" |

Unrecognised phrases fall through to the LLM for conversational handling.

---

## TSP Waypoint GUI

When a `tsp` intent is detected, the waypoint selector opens automatically.

- Click waypoints in the order you want to visit them — visit order is shown on each circle
- Orange lines preview the route
- Press **Start** to publish the tour and close the window
- Press **Clear** to reset the selection

The GUI is a persistent node — it hides after Start and re-opens on the next `tsp` trigger without restarting.

---

## Emotion Engine

The `emotion_node` publishes one of five states to `/emotions`:

| Emotion | Triggered when |
|---|---|
| `thinking` | STT fires — robot is processing before the LLM replies |
| `greeting` | LLM response contains hello / welcome / hi phrases |
| `explaining` | Response is ≥ 60 words or contains narration phrases ("this is", "was built", "history", …) |
| `speaking` | Short conversational reply (default) |
| `idle` | No activity for 15 seconds |

Tune the idle timeout:

```bash
ros2 run turtlebot_llm_control emotion_node --ros-args -p idle_timeout_seconds:=30.0
```

---

## Standalone Tester

```bash
ros2 run turtlebot_llm_control llm_intent_test \
  --provider ollama \
  --model qwen2.5-coder:latest \
  --microphone
```

Useful flags: `--mute`, `--no-llm`, `--list-microphones`, `--mic-device 0`, `--energy-threshold 150`

---

## Pre-launch Checklist

1. `pip install faster-whisper openai`
2. `ollama serve` is running and `curl http://localhost:11434/api/tags` responds
3. `colcon build --packages-select turtlebot_llm_control && source install/setup.bash`
4. Watch `ros2 topic echo /speech_to_text/status` on startup — look for `Loaded faster-whisper 'base' model`
5. Watch `ros2 topic echo /speech/debug` during the demo
