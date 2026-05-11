# TurtleBot LLM Control Demo Guide

## 1. Purpose

This package implements a social tour-guide robot on TurtleBot 3.  The full
pipeline is:

- speech-to-text input (microphone or mock text)
- offline LLM layer powered by **Ollama + Qwen** (no cloud API key required)
- wake / sleep / emergency-stop voice handling
- navigation intent extraction
- SQLite knowledge database with waypoint-linked content
- automatic waypoint arrival explanations during tours
- RAG (Retrieval-Augmented Generation) for visitor questions
- coordinated route recording and playback via Nav2
- voice navigation to named locations in the map

The main showcase:

- wake the robot with a voice phrase
- ask it to navigate somewhere or start a tour
- watch it move and hear it explain each stop automatically
- ask follow-up questions about what you see

---

## 2. Main Files

Core runtime:

- `launch/sim_pillar_nav_demo.launch.py`
- `launch/bringup.launch.py`
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
- `turtlebot_llm_control/knowledge_store.py`
- `turtlebot_llm_control/knowledge_overlay_node.py`
- `turtlebot_llm_control/knowledge_editor.py`
- `turtlebot_llm_control/llm_intent_test.py`
- `speech_locomotion_interface/speech_locomotion_interface/speech_listener.py`

Packaged demo assets:

- `maps/demo/map.yaml` / `map.pgm`
- `config/demo_nav2/burger.yaml` / `waffle.yaml` / `waffle_pi.yaml`
- `rviz/tb3_navigation2.rviz`

---

## 3. Build

```bash
cd /home/karan/in_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select turtlebot_llm_control speech_locomotion_interface
source install/setup.bash
export TURTLEBOT3_MODEL=waffle   # or burger
```

---

## 4. Ollama Setup (offline LLM — no API key needed)

### 4.1 Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Or follow the instructions at https://ollama.com.

### 4.2 Pull the Qwen model

```bash
ollama pull qwen2.5:7b
```

Other good options for lower-memory machines:

```bash
ollama pull qwen2.5:3b       # ~2 GB — faster, less capable
ollama pull qwen2.5:14b      # ~9 GB — higher quality
```

### 4.3 Start the Ollama server

```bash
ollama serve
```

Keep this running in a separate terminal. The server listens on
`http://localhost:11434` by default.

### 4.4 Install the Python client

```bash
pip install ollama
```

### 4.5 Verify

```bash
curl http://localhost:11434/api/tags   # should list pulled models
```

---

## 5. Final Demo Launch

```bash
cd /home/karan/in_ws
source install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot_llm_control sim_pillar_nav_demo.launch.py \
  enable_microphone:=true \
  enable_llm:=true \
  llm_model:=qwen2.5:7b \
  ollama_host:=http://localhost:11434 \
  mute:=false \
  enable_speech_debug:=true
```

What this starts:

- TurtleBot 3 Gazebo world
- Nav2 bringup
- RViz
- speech-to-text node
- speech command node (Ollama/Qwen)
- speech response speaker node
- speech debug node
- behaviour-tree orchestrator (with knowledge store lookup)
- tour recording manager
- knowledge overlay node (map pins for knowledge entries)
- follow-me node
- initial pose publisher for the simulated robot

---

## 6. Knowledge Editor Workflow

The knowledge editor lets you attach information to map waypoints so the robot
can explain each stop during a tour and answer visitor questions using RAG.

### 6.1 Launch the editor

```bash
ros2 run turtlebot_llm_control knowledge_editor
```

Or pass `enable_knowledge_editor:=true` to the launch file.

### 6.2 Creating a waypoint entry

1. Click **New** to clear the form.
2. Set **Key** — a unique slug, e.g. `library` or `pillar_3`.
3. Set **Title** — human-readable name shown in the list and spoken by the robot.
4. Set **Kind** to `place` (for physical locations you navigate to).
5. Enter the **X** and **Y** map coordinates of the waypoint (read from RViz or
   the terminal while driving the robot).
6. Optionally set **Yaw** (radians, facing direction).
7. Fill in **Arrival Speech** — exactly what the robot says when it arrives at
   this waypoint.  Leave blank to auto-generate from the first paragraph of
   Wiki / Notes.
8. Fill in **Wiki / Notes** — rich background content used for RAG.  The robot
   draws on this text when visitors ask questions about the location.
9. Click **Save Entry**.

### 6.3 Arrival speech

- If **Arrival Speech** is filled in, the robot speaks it verbatim when it
  arrives at that waypoint during a tour.
- If it is blank, the robot auto-generates: *"We have arrived at [Title].
  [first paragraph of Wiki/Notes]."*
- Use **Preview Arrival Speech** to hear exactly what the robot will say before
  you run the tour.

### 6.4 RAG question answering

Type a visitor question in the **Ask a Question** box and press **Ask**.
Ollama searches the knowledge database and returns a grounded answer.  This
same pipeline is used when a visitor speaks a question to the robot during a
tour.

### 6.5 Linking artifacts to places

- Create a `place` entry for the location (with x, y coords).
- Create an `artifact` entry for the exhibit.
- Set the artifact's **Location key** to the place's key.
- The artifact inherits the place's coordinates automatically.

---

## 7. Tour Recording Flow

1. Say **"start recording"** — recording mode begins; a teleop terminal opens.
2. Drive the robot manually with `w`, `a`, `s`, `d` to trace the tour route.
3. Press `r` then `Enter` in the teleop terminal to publish the route label to
   `/save_tour_command`.
4. Press `Esc` in the teleop terminal to stop and return to autonomy.
5. Say **"start tour"** to replay the recorded route.

During replay the robot navigates to each recorded waypoint in sequence, then
looks up the nearest knowledge entry (within 2 m) and speaks the arrival
explanation before moving to the next stop.

---

## 8. Standalone Tester

Test speech / LLM behaviour without Gazebo:

```bash
ros2 run turtlebot_llm_control llm_intent_test \
  --model qwen2.5:7b \
  --ollama-host http://localhost:11434 \
  --microphone
```

Useful flags:

- `--mute`
- `--no-llm`
- `--wake-timeout 45.0`

---

## 9. Voice Behaviour

Wake phrases:

- `hey pepper`
- `hi pepper`
- `hello pepper`
- `pepper`

After wake-up the robot stays active for 45 seconds of inactivity; each
utterance resets the timer.

Sleep commands:

- `good night pepper`
- `sleep pepper`
- `pepper sleep`

Emergency stop:

- `stop`
- `stop stop`
- `stop now`
- `emergency stop`

---

## 10. Demo Spoken Commands

Navigation:

```
hey pepper
go to pillar 1
go to the library
take me to pillar 5
```

Tour:

```
start recording
[drive the route manually]
stop recording
start tour
stop tour
```

Knowledge questions (asked during or outside a tour):

```
tell me about this room
what is the history of this library?
describe what we can see here
```

---

## 11. ROS Topics Reference

| Topic | Description |
|---|---|
| `/speech/text` | Transcribed speech text |
| `/speech/intent` | JSON intent from the LLM |
| `/speech/response` | Text the robot speaks aloud |
| `/speech/debug` | Aggregated pipeline diagnostics |
| `/speech_to_text/status` | STT node health |
| `/tour/status` | Current tour / task state |
| `/route/record` | Start / stop recording |
| `/route/data` | Saved waypoint list |
| `/save_tour_command` | Trigger route save |
| `/knowledge_markers` | RViz map pins for knowledge entries |

One-line pipeline monitor:

```bash
ros2 topic echo /speech/debug
```

---

## 12. TTS Backends

The speech response node tries these in order:

1. `spd-say` (Linux Speech Dispatcher — recommended)
2. `espeak`
3. `say` (macOS)

Install on Ubuntu:

```bash
sudo apt install speech-dispatcher espeak
```

---

## 13. Known Runtime Noise

Nav2 / AMCL log messages like `Message Filter dropping message` or TF
timestamp warnings are normal during startup while Gazebo, TF, localisation,
and Nav2 are settling.  Focus on:

- `/speech/debug` showing the correct text and intent
- The robot speaking its arrival explanation at each stop
- The robot accepting navigation goals and moving

---

## 14. Quick Checklist

1. `ollama serve` is running in a separate terminal
2. `ollama pull qwen2.5:7b` has completed
3. `pip install ollama` is done
4. `colcon build ...` succeeded
5. `source install/setup.bash`
6. `export TURTLEBOT3_MODEL=waffle`
7. Launch `sim_pillar_nav_demo.launch.py`
8. Watch `ros2 topic echo /speech/debug`
9. Open the knowledge editor and add waypoint entries with arrival speech

---

## 15. One-Line Demo Reminder

```
hey pepper → go to pillar 1 → robot navigates → arrives → explains the stop → visitor asks question → RAG answer
```
