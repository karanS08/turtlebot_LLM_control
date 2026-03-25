# TurtleBot LLM Control Guide

## 1. Scope

This package provides:

- speech-to-text input path
- predefined command recognition
- optional LLM-backed conversation with personality
- behavior-tree-based action orchestration
- Nav2 goal triggering
- follow mode for a colored target

## 2. Core Features

- `speech_to_text_node`: microphone-to-text bridge, plus `/speech/mock_text` for testing
- `speech_command_node`: converts user text into either `no_action` or a behavior-tree action
- `bt_orchestrator_node`: runs the task logic and triggers ROS2 actions/topics
- `follow_me_node`: follows a selected colored target

## 3. Build

```bash
cd /home/karan/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
```

## 4. Main Launch Flags

- `hardware:=false`
  Use simulation. Gazebo starts where applicable. `use_sim_time=true`.

- `hardware:=true`
  Use the real robot. Gazebo is skipped. `use_sim_time=false`.

- `enable_microphone:=true`
  Enables microphone speech recognition in `speech_to_text_node`.

- `enable_llm:=true`
  Enables LLM-backed conversation in `speech_command_node`.

- `llm_provider:=groq`
  Selects the LLM provider. Current supported values: `groq`, `openai`.

- `llm_model:=llama-3.3-70b-versatile`
  Sets the model name used by the conversational layer.

- `bin_tuning_mode:=true`
  Opens OpenCV HSV tuning controls for the green bin detector.

- `image_topic:=/camera/image_raw`
  Overrides the camera topic.

## 5. Runtime Requirements

### Simulation

- Gazebo
- Cartographer or Nav2 launched through this package
- no microphone required

### Real Robot

- TurtleBot base bringup already running
- camera driver already running
- TF tree available
- Cartographer for mapping mode
- Nav2 for remembered-bin navigation mode

### LLM Mode

- for Groq:
  `GROQ_API_KEY` in the shell, or a local untracked `api.key` beside [api.key.example](/home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/api.key.example)
  Python `groq` package available

- for OpenAI:
  `OPENAI_API_KEY` in the shell
  Python `openai` package available

If the LLM client is unavailable, the package falls back to rule-based commands and simple canned conversation replies.

## 6. Stage 1: Mapping And Bin Memory

### Simulation

```bash
cd /home/karan/ros2_ws
source install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot_llm_control autonomous_bin_mission.launch.py hardware:=false
```

### Real Robot

```bash
cd /home/karan/ros2_ws
source install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot_llm_control autonomous_bin_mission.launch.py hardware:=true image_topic:=/camera/image_raw
```

### Real Robot With Green Calibration

```bash
cd /home/karan/ros2_ws
source install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot_llm_control autonomous_bin_mission.launch.py hardware:=true image_topic:=/camera/image_raw bin_tuning_mode:=true
```

### What Starts

- speech-to-text bridge
- conversational command layer
- reactive navigation
- exploration manager
- bin detector
- bin memory
- follow controller
- behavior-tree orchestrator
- Cartographer
- Gazebo only when `hardware:=false`

## 7. Speech Input Paths

### Mock Speech

Use this in simulation or testing:

```bash
ros2 topic pub --once /speech/mock_text std_msgs/msg/String "{data: 'start exploring'}"
ros2 topic pub --once /speech/mock_text std_msgs/msg/String "{data: 'here is the bin'}"
ros2 topic pub --once /speech/mock_text std_msgs/msg/String "{data: 'go to lab'}"
ros2 topic pub --once /speech/mock_text std_msgs/msg/String "{data: 'stop navigation'}"
```

### Direct Text Injection

```bash
ros2 topic pub --once /speech/text std_msgs/msg/String "{data: 'follow me'}"
ros2 topic pub --once /speech/text std_msgs/msg/String "{data: 'go to the red bin'}"
```

### Microphone Mode

```bash
export GROQ_API_KEY=your_key_here
ros2 launch turtlebot_llm_control autonomous_bin_mission.launch.py hardware:=true enable_microphone:=true enable_llm:=true llm_provider:=groq llm_model:=llama-3.3-70b-versatile
```

If you create a local `api.key` beside [api.key.example](/home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/api.key.example), the node can use that automatically.

### Standalone LLM Intent Test

Purpose:

- print only the resolved intent in the terminal
- speak the assistant reply through local speakers
- debug Groq intent classification without launching the full robot stack

Command:

```bash
cd /home/karan/ros2_ws
source install/setup.bash
ros2 run turtlebot_llm_control llm_intent_test --provider groq --model llama-3.3-70b-versatile
```

Optional flags:

- `--microphone`
- `--mute`
- `--wake-timeout 45.0`
- `--api-key-path /path/to/key`
- `--key /path/to/key`
- `--no-llm`

Behavior:

- terminal prints only the final intent such as `follow`, `navigate`, or `no_action`
- assistant reply is spoken through `spd-say`, `espeak`, or `say` if available
- in ROS launches, spoken replies are played from `/speech/response` by `speech_response_node`
- in `--microphone` mode, Pepper wakes on `hey pepper`, `hi pepper`, or `hello pepper`
- saying only the wake phrase wakes Pepper silently for 45 seconds by default
- while awake, Pepper listens and replies normally without needing another wake phrase
- each new utterance resets the timer, so Pepper sleeps only after 45 seconds of silence
- saying `good night pepper` or `sleep pepper` sends `stop` and puts Pepper back to sleep
- saying `emergency stop`, `stop stop`, or `stop now` sends an immediate global `stop`
- the script can use a local untracked `api.key` beside [api.key.example](/home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/api.key.example) automatically

## 9. Command Behavior

The conversational layer produces one of two outcomes:

- `no_action`
  General conversation only. The robot replies verbally and does nothing physically.

- action intent
  The robot replies verbally and triggers a behavior-tree action.

## 10. Pillar Demo In Gazebo

For a simple voice-navigation showcase in simulation, the TurtleBot3 world already includes pillar-like obstacles and the speech layer can map requests such as `go to pillar 1` or `go to pillar five` into Nav2 goals.

Setup:

```bash
cd /home/karan/ros2_ws
export TURTLEBOT3_MODEL=burger
source install/setup.bash
ros2 launch turtlebot_llm_control sim_pillar_nav_demo.launch.py \
  enable_microphone:=true \
  enable_llm:=true \
  llm_provider:=groq \
  llm_model:=llama-3.3-70b-versatile \
  llm_api_key_path:=/home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/api.key \
  mute:=false
```

Example spoken commands:

- `hey pepper`
- `go to pillar 1`
- `go to pillar 5`
- `go to pillar five`
- `stop`

Notes:

- the demo world is the standard TurtleBot3 Gazebo world
- Nav2 is launched against the packaged demo map and packaged Nav2 parameters in this repository
- an initial pose is published automatically for the simulated robot spawn point

Supported action families include:

- follow
- is_alive
- stop
- stop navigation
- navigate
- go to remembered bin
- start exploring
- stop exploring
- inspect bin
- pause
- resume
- manual override on
- manual override off
- start tour

## 10. Bin Workflow

The bin detector is guided, not always-on.

### Recommended Flow

1. Move the robot near the green bin.
2. Say `here is the bin`.
3. Keep the bin steady in view.
4. Wait for a stable confirmation.
5. The bin is saved into memory.

### Direct Detector Arming

```bash
ros2 topic pub --once /bin_detector/control std_msgs/msg/String "{data: 'arm:green'}"
```

### Important Behavior

- the detector waits for an explicit cue
- the detector requires multiple stable frames before publishing `found=true`
- this reduces hallucinated bin saves

## 11. Follow Workflow

### Start Following

```bash
ros2 topic pub --once /speech/text std_msgs/msg/String "{data: 'follow me'}"
```

### Direct Follow Control

```bash
ros2 topic pub --once /follow_me/control std_msgs/msg/String "{data: 'start:yellow'}"
ros2 topic pub --once /follow_me/control std_msgs/msg/String "{data: 'stop'}"
```

## 12. Memory And Visualization

### Persistent Memory File

```bash
~/.ros/turtlebot_llm_control/bin_memory.json
```

### RViz

- add a `MarkerArray` display
- set topic to `/bin_memory/markers`

### Marker Meaning

- colored spheres: remembered bins
- text labels: names like `green_bin_01`
- line strips: breadcrumb paths

## 14. Key Topics

- `/speech/mock_text`
- `/speech/text`
- `/speech/intent`
- `/speech/response`
- `/speech/debug`
- `/speech_to_text/status`
- `/tour/status`
- `/reactive_nav/status`
- `/exploration/status`
- `/bin_detector/status`
- `/bin_detector/detection`
- `/bin_memory/state`
- `/bin_memory/status`
- `/bin_memory/markers`
- `/follow_me/status`

## 15. Debug Commands

```bash
ros2 topic echo /speech_to_text/status
ros2 topic echo /speech/debug
ros2 topic echo /speech/response
ros2 topic echo /tour/status
ros2 topic echo /reactive_nav/status
ros2 topic echo /exploration/status
ros2 topic echo /bin_detector/status
ros2 topic echo /bin_detector/detection
ros2 topic echo /bin_memory/status
ros2 topic echo /follow_me/status
```

## 16. Manual Override

### Enable

```bash
ros2 topic pub --once /speech/text std_msgs/msg/String "{data: 'manual override'}"
```

or

```bash
ros2 topic pub --once /manual_override/control std_msgs/msg/String "{data: 'on'}"
```

### Disable

```bash
ros2 topic pub --once /speech/text std_msgs/msg/String "{data: 'resume autonomous'}"
```

or

```bash
ros2 topic pub --once /manual_override/control std_msgs/msg/String "{data: 'off'}"
```

## 17. Compliance Summary

This package now includes:

- speech-to-text integration
- predefined command recognition
- command-to-action mapping
- ROS2 navigation goal triggering
- verbal responses
- basic behavior-tree control
- general conversation with `no_action` or allowed actions
