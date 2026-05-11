# Workspace Summary

## 1. Objective

This workspace contains a minimal ROS 2 robot project for a social tour guide robot.  The main objective is to keep the workspace focused on:

- `turtlebot_llm_control`: the main LLM-driven TurtleBot control package.
- `turtlebot_social_guide`: the social guide support package that provides tour recording, visualisation, and speech-locomotion interfaces.

All LLM inference is **fully offline** using a local **Ollama** server running **Qwen 2.5**.  No cloud API keys or internet connection are required.

The workspace was intentionally cleaned to remove unrelated experimental branches and stale build artefacts.

---

## 2. Workspace layout

### Root packages

- `src/turtlebot_LLM_control` — custom LLM-driven robot control package.
- `src/turtlebot_social_guide` — support package with social tour guide components.

### Important subdirectories in `turtlebot_LLM_control`

- `src/turtlebot_LLM_control/package.xml`
- `src/turtlebot_LLM_control/setup.py`
- `src/turtlebot_LLM_control/setup.cfg`
- `src/turtlebot_LLM_control/GUIDE.md`
- `src/turtlebot_LLM_control/README.md`
- `src/turtlebot_LLM_control/launch/bringup.launch.py`
- `src/turtlebot_LLM_control/launch/sim_pillar_nav_demo.launch.py`
- `src/turtlebot_LLM_control/config/demo_nav2/`
- `src/turtlebot_LLM_control/maps/demo/`
- `src/turtlebot_LLM_control/rviz/tb3_navigation2.rviz`
- `src/turtlebot_LLM_control/turtlebot_llm_control/` (Python package)

### Important subdirectories in `turtlebot_social_guide`

- `src/turtlebot_social_guide/src/speech_locomotion_interface/`
- `src/turtlebot_social_guide/src/tour_manager/`
- `src/turtlebot_social_guide/src/social_robot_interfaces/`
- `src/turtlebot_social_guide/src/robot_tour/`

---

## 3. Package descriptions

### 3.1 `turtlebot_llm_control`

This is the main package.  It contains the full speech, navigation, tour, knowledge, and LLM system for the TurtleBot.

Key files and their roles:

- `package.xml` — ROS 2 package manifest; declares all dependencies.
- `setup.py` — Python package installer; registers every node as a console entry point.
- `launch/bringup.launch.py` — starts the core LLM control nodes for hardware or simulation.
- `launch/sim_pillar_nav_demo.launch.py` — starts Gazebo, Nav2, RViz, and the full LLM stack.

Python module files and responsibilities:

| File | Role |
|---|---|
| `audio_utils.py` | Local text-to-speech helper (spd-say / espeak) |
| `behavior_tree.py` | Lightweight behaviour tree used by the orchestrator |
| `bt_orchestrator_node.py` | **Main orchestrator** — intent → Nav2 goals, tour loop, waypoint explanation |
| `follow_me_node.py` | Colour-blob visual tracking; publishes `/cmd_vel` |
| `knowledge_editor.py` | Tkinter GUI for managing the SQLite waypoint knowledge database |
| `knowledge_overlay_node.py` | Publishes RViz map markers for knowledge entries |
| `knowledge_store.py` | SQLite knowledge database, search engine, RAG context builder |
| `llm_dialogue.py` | **Offline LLM interface** — Ollama/Qwen backend for intent and RAG |
| `llm_intent_test.py` | CLI tool for testing the LLM intent pipeline manually |
| `models.py` | Shared data classes (IntentToken, TaskState, DialogueMemory, etc.) |
| `predefined_commands.py` | Hard-coded speech command patterns |
| `sim_initial_pose_node.py` | Publishes initial pose to `/initialpose` for AMCL in simulation |
| `speech_command_node.py` | Converts `/speech/text` → `/speech/intent` via Ollama |
| `speech_debug_node.py` | Aggregates speech pipeline topics into `/speech/debug` |
| `speech_parser.py` | Rule-based intent parsing (used before LLM) |
| `speech_response_node.py` | Converts `/speech/response` text to spoken audio |
| `speech_to_text_node.py` | Microphone / mock-text → `/speech/text` with wake-word gating |
| `tour_recording_manager.py` | Records robot poses into waypoint lists during teleoperation |
| `tour_teleop_session.py` | Keyboard teleoperation helper for route recording |
| `wake_word.py` | Wake-word detection and emergency stop logic |

### 3.2 `turtlebot_social_guide`

Support package for the LLM control package.

Key components:

- `tour_manager/tour_saver.py` — publishes a map pose when a save command is received.
- `tour_manager/tour_manager_service.py` — ROS 2 service for tour retrieval and save.
- `tour_manager/waypoint_visualizer.py` — publishes visualisation markers for saved tour waypoints.
- `speech_locomotion_interface/speech_listener.py` — listens to `/speech/intent` and drives navigation directly via `nav2_simple_commander`.
- `social_robot_interfaces/srv/Tours.srv` — custom service definition.
- `robot_tour/plugins/talk_at_waypoint.cpp` — Nav2 BT plugin that fires speech at waypoints.

---

## 4. Install and build flow

### 4.1 Ollama setup (required — runs the local LLM)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model (one-time, ~4 GB)
ollama pull qwen2.5:7b

# Start the server (keep running in a separate terminal)
ollama serve

# Install the Python client
pip install ollama
```

### 4.2 Build commands

```bash
cd /home/karan/in_ws
colcon build
source install/setup.bash
```

### 4.3 Launch commands

Main launch files:

- `ros2 launch turtlebot_llm_control bringup.launch.py` — core LLM control stack only.
- `ros2 launch turtlebot_llm_control sim_pillar_nav_demo.launch.py` — full Gazebo + Nav2 + LLM demo.

Individual nodes:

- `ros2 run turtlebot_llm_control knowledge_editor` — open the knowledge database GUI.
- `ros2 run turtlebot_llm_control llm_intent_test` — test LLM intent parsing interactively.
- `ros2 run turtlebot_llm_control speech_debug_node` — monitor the speech pipeline.

---

## 5. ROS 2 data flow

### 5.1 Speech stack flow

1. `speech_to_text_node` — mic/mock → `/speech/text` (gated by wake word).
2. `speech_command_node` — `/speech/text` → Ollama/Qwen → `/speech/intent` (JSON).
3. `bt_orchestrator_node` — `/speech/intent` → Nav2 goals, tour control, knowledge lookup.
4. `speech_response_node` — `/speech/response` → spoken audio via TTS.
5. `speech_debug_node` — aggregates all pipeline topics → `/speech/debug`.

### 5.2 Navigation and tour flow

- `bt_orchestrator_node` sends `NavigateToPose` action goals to Nav2.
- `sim_initial_pose_node` seeds AMCL with an initial pose on simulation start.
- `tour_recording_manager` records `/amcl_pose` during teleoperation → waypoint lists.
- On tour replay, the orchestrator navigates to each waypoint, then calls
  `KnowledgeStore.get_nearest_entry(x, y)` to look up the closest knowledge
  entry and speaks its `arrival_speech` (or auto-generates from the first
  paragraph of the entry's content).
- After the explanation, it waits for the estimated speech duration, then
  moves to the next waypoint.
- `follow_me_node` uses colour-blob tracking to follow a person visually.

### 5.3 Knowledge system

- **Database**: SQLite at `~/.local/share/turtlebot_llm_control/knowledge.db`.
- **Schema**: `key`, `title`, `kind`, `location_key`, `x`, `y`, `yaw`, `tags`, `arrival_speech`, `content`, `updated_at`.
- **`arrival_speech`**: exact text the robot speaks on arriving at this waypoint (new field).
- **`content`**: rich Markdown notes used for RAG question answering.
- **`knowledge_editor`**: Tkinter GUI — fill in coordinates, arrival speech, and wiki notes; press **Preview Arrival Speech** to verify before running the tour.
- **`knowledge_overlay_node`**: publishes RViz markers for all geotagged entries.
- **RAG**: when a visitor asks a question, `speech_command_node` calls Ollama with the top-k matching knowledge entries as context and returns a grounded answer.

---

## 6. LLM usage (Ollama — fully offline)

The LLM system is implemented in `llm_dialogue.py` and backed by a local
Ollama server.  No internet connection or API key is required.

### Provider

| Item | Value |
|---|---|
| Engine | Ollama (local) |
| Default model | `qwen2.5:7b` |
| Server endpoint | `http://localhost:11434` |
| Python client | `pip install ollama` |

### What the LLM is used for

1. **Intent classification** when rule-based parsing cannot decide.
2. **Personalised response rewriting** — makes replies sound natural.
3. **RAG question answering** — answers visitor questions using knowledge database content as context.

### Key functions in `LLMDialogueEngine`

- `generate_llm_token(utterance)` — returns a JSON intent object.
- `generate_personalized_response(parsed)` — rewrites a response in a friendly tone.
- `generate_knowledge_response(utterance)` — builds context from the knowledge store and asks Ollama.

### Fallback

If Ollama is not running or `pip install ollama` has not been done, the system
falls back to rule-based responses.  Basic navigation commands continue to work.

---

## 7. Dependencies and requirements

### ROS 2 dependencies in `turtlebot_llm_control`

`ament_python`, `rclpy`, `std_msgs`, `std_srvs`, `geometry_msgs`, `nav_msgs`,
`nav2_msgs`, `action_msgs`, `sensor_msgs`, `tf2_ros`, `tf_transformations`,
`visualization_msgs`, `launch`, `launch_ros`, `ament_index_python`,
`speech_locomotion_interface` (runtime), `tour_manager` (runtime).

### Python (pip) dependencies

| Package | Required? | Purpose |
|---|---|---|
| `ollama` | **Required for LLM** | Offline Qwen inference via local Ollama server |
| `SpeechRecognition` | Optional | Microphone-based speech-to-text |
| `opencv-python` | Recommended | Person-following colour tracking |
| `tkinter` | Standard | Knowledge editor GUI |
| `sqlite3` | Standard | Knowledge database |

### Hardware and simulation

- `sim_pillar_nav_demo.launch.py` uses Gazebo from `turtlebot3_gazebo` and Nav2 from `nav2_bringup`.
- `bringup.launch.py` supports both hardware (`hardware:=true`) and simulation.

---

## 8. Important warnings and cleanup status

- The workspace contains only two source packages: `turtlebot_llm_control` and `turtlebot_social_guide`.
- All Groq and OpenAI cloud dependencies have been removed; Ollama is the sole LLM backend.
- Stale `build/`, `install/`, `log/` directories were removed from the workspace root.
- The knowledge database has a new `arrival_speech` column (auto-migrated from older databases).

---

*Generated documentation for the `/home/karan/in_ws` workspace.*
