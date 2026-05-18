# ARIA Social Tour Guide Robot — Developer Guide

## Architecture Overview

```
┌──────────────────────── turtlebot_llm_control ─────────────────────────────┐
│                                                                               │
│  [speech_to_text_node]      /speech/text      [speech_command_node]          │
│   Faster-Whisper + VAD  ─────────────────▶    RobotBrain (Ollama/Qwen2.5)   │
│   /speech/mock_text ──▶                        MemoryManager (3-layer)       │
│   /robot/expression ◀──                     ──/speech/intent──▶              │
│                                             ◀──/tour/status                  │
│                                                                               │
│  [bt_orchestrator_node]  ◀──/speech/intent                                  │
│   Behaviour Tree (BT)    ──▶ /speech/response  ──▶ [speech_response_node]   │
│                          ──▶ /tour/status          (TTS: espeak/spd-say)    │
│                          ──▶ /robot/expression  ──▶ Hayden's gesture node   │
│                          ──▶ /follow_me/control                              │
│                          ──▶ /manual_override/control                        │
│                          ──▶ Nav2: /navigate_to_pose  (single-point nav)     │
│                          ──▶ Nav2: /follow_waypoints  (tour execution)       │
│                          ──▶ service: tour_retrieve   (social_guide)         │
│                                                                               │
│  [speech_debug_node]  aggregates all speech topics → /speech/debug           │
└───────────────────────────────────────────────────────────────────────────────┘

┌──────────────── tour_maker  (bridge, non-invasive) ─────────────────────────┐
│                                                                               │
│  [waypoint_recorder]  ──▶ /save_tour_command  ──▶ (social_guide)            │
│  [tour_planner]       ◀── tour_retrieve service   (social_guide)            │
│                       ◀── /map topic                                         │
│                       ──▶ ~/tours/tourN.csv        (read by bt_orchestrator) │
└───────────────────────────────────────────────────────────────────────────────┘

┌──────────── turtlebot_social_guide  (DO NOT MODIFY) ────────────────────────┐
│                                                                               │
│  [tour_manager_service]  ◀── /save_tour  (PoseStamped)                      │
│                          ──▶ service: tour_retrieve                          │
│  [tour_saver]            ◀── /save_tour_command  (String)                   │
│                          ──▶ TF lookup ──▶ /save_tour                       │
│  [tour_guide]            ◀── /tour_command  ──▶ /follow_waypoints           │
│  [subtour]               ◀── /tsp_command   ──▶ /follow_waypoints (TSP)     │
│  [talk_at_waypoint]          Nav2 plugin: fires at each waypoint             │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Package Layout

### `turtlebot_llm_control/`
```
turtlebot_llm_control/
├── package.xml                    ROS2 package manifest
├── setup.py                       Python build config; entry points
├── setup.cfg                      Install script paths
├── launch/
│   └── bringup.launch.py          Main launch file for all LLM nodes
└── turtlebot_llm_control/
    ├── models.py                  Shared data models: TaskState, IntentToken, RobotExpression
    ├── wake_word.py               Wake phrase detection and text normalisation
    ├── speech_parser.py           Rule-based fallback intent parser (no LLM)
    ├── predefined_commands.py     Fuzzy-match command whitelist for STT node
    ├── audio_utils.py             TTS helper (espeak/spd-say)
    ├── behavior_tree.py           Minimal BT framework (SequenceNode, FallbackNode, etc.)
    ├── memory_manager.py          3-layer persistent memory for RobotBrain
    ├── llm_brain.py               RobotBrain: Ollama/Qwen2.5 chain-of-thought intent engine
    ├── speech_to_text_node.py     STT node: Faster-Whisper + wake-word gating
    ├── speech_command_node.py     Calls RobotBrain, publishes IntentToken + /robot/expression
    ├── bt_orchestrator_node.py    Central BT controller: navigation, tours, expressions
    ├── speech_response_node.py    Speaks /speech/response via system TTS
    └── speech_debug_node.py       Aggregates all speech topics to /speech/debug
```

### `tour_maker/`
```
tour_maker/
├── package.xml
├── setup.py
├── setup.cfg
├── launch/
│   └── tour_maker.launch.py       Launches waypoint_recorder
└── tour_maker/
    ├── __init__.py
    ├── waypoint_recorder.py       Terminal node: R+Enter → /save_tour_command
    └── tour_planner.py            matplotlib GUI: map+waypoints → tour CSV
```

---

## ROS2 Interface Reference

| Topic / Service / Action | Type | Publisher | Subscriber(s) | Purpose |
|---|---|---|---|---|
| `/speech/text` | String | speech_to_text_node | speech_command_node | Raw transcribed text after wake-word gate |
| `/speech/mock_text` | String | External / test | speech_to_text_node | Inject text without a microphone |
| `/speech_to_text/status` | String | speech_to_text_node | speech_debug_node | STT status messages |
| `/speech/intent` | String (JSON) | speech_command_node | bt_orchestrator_node | Serialised IntentToken |
| `/speech/response` | String | bt_orchestrator_node | speech_response_node, speech_debug_node | Text for ARIA to speak aloud |
| `/speech/debug` | String | speech_debug_node | — | Aggregated debug stream |
| `/robot/expression` | String | speech_to_text_node, speech_command_node, bt_orchestrator_node | Hayden's gesture node | Current robot expression state |
| `/tour/status` | String (JSON) | bt_orchestrator_node | speech_command_node | Current state passed as context to LLM |
| `/follow_me/control` | String | bt_orchestrator_node | follow_me subsystem | "start:color" / "stop" |
| `/manual_override/control` | String | bt_orchestrator_node | teleop subsystem | "on" / "off" |
| `/save_tour_command` | String | tour_maker/waypoint_recorder | social_guide/tour_saver | Trigger waypoint save |
| `/save_tour` | PoseStamped | social_guide/tour_saver | social_guide/tour_manager | Pose to persist to DB |
| `/map` | OccupancyGrid | Nav2 | tour_maker/tour_planner | Environment map for visualisation |
| `/amcl_pose` | PoseWithCovarianceStamped | Nav2 AMCL | waypoint_recorder, social_guide/subtour | Current robot localisation |
| `tour_retrieve` (service) | social_robot_interfaces/Tours | social_guide/tour_manager | bt_orchestrator_node, tour_planner | Fetch all saved PoseStamped waypoints |
| `/navigate_to_pose` (action) | nav2_msgs/NavigateToPose | bt_orchestrator_node | Nav2 | Single-destination navigation |
| `/follow_waypoints` (action) | nav2_msgs/FollowWaypoints | bt_orchestrator_node | Nav2 | Ordered multi-stop tour execution |

---

## Tunable Parameters

### `speech_to_text_node`
| Parameter | Default | Options / Range | Effect |
|---|---|---|---|
| `enable_microphone` | `false` | `true` / `false` | Use real mic or `/speech/mock_text` |
| `require_wake_word` | `true` | `true` / `false` | Enforce "Hey ARIA" before processing commands |
| `wake_command_window_seconds` | `45.0` | `5.0 – 120.0` | How long the robot stays "awake" after wake word |
| `whisper_model` | `"base"` | `tiny` / `base` / `small` / `medium` / `large` | Accuracy vs. CPU speed tradeoff |
| `language` | `"en"` | any Whisper language code | Transcription language |
| `sample_rate` | `16000` | `8000` / `16000` / `44100` | Audio sample rate (Hz) |
| `chunk_duration_secs` | `3.0` | `1.0 – 10.0` | Audio chunk length sent to Whisper |

### `speech_command_node`
| Parameter | Default | Options / Range | Effect |
|---|---|---|---|
| `enable_llm` | `true` | `true` / `false` | Use Ollama or fall back to rule-based only |
| `ollama_model` | `"qwen2.5"` | any installed Ollama model | LLM model for intent parsing |
| `ollama_url` | `"http://localhost:11434/api/chat"` | URL | Ollama server address |
| `memory_file` | `"~/.ros/robot_memory.json"` | path | Where persistent memory is stored |

### `bt_orchestrator_node`
| Parameter | Default | Options / Range | Effect |
|---|---|---|---|
| `tours_dir` | `"~/tours"` | path | Directory containing tour CSV files |

---

## LLM Brain Internals (`llm_brain.py`)

### How it works

`RobotBrain.think(utterance, context)` is called for every transcribed speech input. It:

1. Builds a **system prompt** containing:
   - ARIA's full capability list (what she can and cannot do)
   - Current state (e.g. `TOURING`, `IDLE`)
   - Available tours (read from `~/tours/*.csv`)
   - Available waypoints (injected from `/tour/status`)
   - Memory context (last 3 session summaries, learned nicknames, semantic facts)

2. Prepends the last 20 conversation turns as Ollama chat history.

3. Sends to Ollama with `"format": "json"` so the output is always structured.

4. The model is prompted to **reason before acting** (chain-of-thought in the `reasoning` field):
```json
{
  "reasoning": "The user said 'take me to the paintings'. Waypoint 3 is art_gallery — close match.",
  "intent": "navigate",
  "label": "3",
  "location": "art_gallery",
  "confidence": 0.92,
  "response": "Of course! Let me take you to the art gallery."
}
```

5. If `confidence < 0.6`, ARIA asks a clarifying question instead of acting.

6. If Ollama is unreachable (timeout 8 s), falls back to `speech_parser.parse_utterance()`.

### Valid intent values
`navigate` | `start_tour` | `save_waypoint` | `explain` | `follow` | `stop` | `pause` | `resume` | `dock` | `is_alive` | `no_action`

### Checking Ollama
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Pull the default model
ollama pull qwen2.5

# List installed models
ollama list
```

---

## Memory System (`memory_manager.py`)

Three memory layers are stored in one JSON file:

| Layer | Key in JSON | Lifetime | Content |
|---|---|---|---|
| Working | *(in-process only)* | Session | Last 20 conversation turns |
| Episodic | `"sessions"` | Persistent (last 10) | Session summaries |
| Semantic | `"facts"`, `"waypoint_nicknames"` | Persistent | Learned facts and nicknames |

**File location:** `~/.ros/robot_memory.json`

**To reset memory:** `rm ~/.ros/robot_memory.json`

**Example file:**
```json
{
  "sessions": [
    {"date": "2025-05-16T10:00:00", "summary": "Completed tour1 with 4 visitors. Stop 3 was most popular."}
  ],
  "facts": ["Visitors prefer slower explanations at stop 3"],
  "waypoint_nicknames": {
    "paintings room": 3,
    "the fountain area": 6
  }
}
```

---

## Tour CSV Format

Tour files live in `~/tours/` by default. Each file is named `tourN.csv` or with a custom name.

```csv
# tour: entrance_gallery
# saved: 2025-05-16T12:00:00
# waypoints: 5
3,"Welcome to the main entrance! This building was constructed in 1923."
1,"Here you can see the historical collection spanning three centuries."
7,"This is the art gallery, featuring works by local artists."
2,
5,"This concludes our tour. Thank you for visiting!"
```

- **Column 1:** Integer waypoint index (0-based, matching the order returned by `tour_retrieve`)
- **Column 2:** Optional description ARIA speaks on arrival (empty = silent stop)
- Lines starting with `#` are comments and are ignored
- Filename (without `.csv`) is the tour name used in voice commands

The bt_orchestrator tries both `{name}.csv` and `tour{name}.csv` when loading.

---

## Expression State Machine

The `/robot/expression` topic is published whenever ARIA changes what she is doing. This is the interface boundary for Hayden's gesture and display subsystem.

| Value | Published when | Suggested Pepper behaviour |
|---|---|---|
| `IDLE` | No active task | Gentle swaying, attract animation |
| `LISTENING` | Wake word detected | Head turns toward speaker |
| `THINKING` | LLM is processing speech | Head tilt, "thinking" animation |
| `TALKING` | ARIA is speaking a response | Expressive hand gestures, mouth sync |
| `NAVIGATING` | Moving toward a destination | Forward-facing, "follow me" wave |
| `EXPLAINING` | Speaking at a tour waypoint | Point/gesture toward exhibit, screen shows image |

**How to subscribe (Python example):**
```python
self.create_subscription(String, '/robot/expression', self.expression_cb, 10)

def expression_cb(self, msg):
    state = msg.data  # e.g. "THINKING"
    # call Pepper animation API here
```

---

## Adding a New Intent

1. **`speech_parser.py`** — add a `_cmd(t, "your phrase")` rule and return a new `IntentToken(intent="your_intent", …)`.

2. **`models.py`** — if the intent requires a new robot state, add it to `TaskState`.

3. **`bt_orchestrator_node.py`** — add a handler inside `_apply_intent()`:
   ```python
   if intent == "your_intent":
       self._set_expression(RobotExpression.NAVIGATING)
       # your logic here
       self._say(token.response)
       return
   ```

4. **`predefined_commands.py`** — add a sample phrase for fuzzy matching.

5. **`llm_brain.py`** — update `_CAPABILITIES` to mention the new intent so the LLM knows about it.

---

## Extending to Pepper

- Subscribe to `/robot/expression` in a new Pepper-specific ROS2 node and map each state to a Pepper SDK animation call.
- `/speech/response` contains the text ARIA should speak — replace the `speech_response_node` espeak call with Pepper's `ALTextToSpeech` service.
- The `_sync_gesture_stub()` method in `bt_orchestrator_node.py` is an intentional no-op placeholder — call a Pepper gesture service from there when ready.
- `/talk_command` (from social_guide's `talk_at_waypoint` plugin) also sends text to be spoken at each tour waypoint.

---

## Troubleshooting

| Problem | Diagnosis command | Fix |
|---|---|---|
| ARIA says "basic mode" | `curl http://localhost:11434/api/tags` | Run `ollama serve` in a terminal |
| Qwen model not found | `ollama list` | Run `ollama pull qwen2.5` |
| STT node error: faster-whisper | `python3 -c "import faster_whisper"` | `pip install faster-whisper` |
| STT node error: sounddevice | `python3 -c "import sounddevice"` | `pip install sounddevice` |
| tour_retrieve not available | `ros2 service list \| grep tour` | Launch social_guide nodes first |
| Tour CSV not found | `ls ~/tours/` | Run `tour_planner` to create the CSV |
| Build errors (social_robot_interfaces) | `ros2 pkg list \| grep social` | Build social_guide: `colcon build --packages-select social_robot_interfaces` |
| Navigation goal rejected | `ros2 topic echo /navigate_to_pose/_action/status` | Check Nav2 is running and robot is localised |
