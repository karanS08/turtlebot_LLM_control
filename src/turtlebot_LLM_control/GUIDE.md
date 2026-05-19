# TurtleBot LLM Control Demo Guide

## 1. Purpose

This package is now focused on one final demo:

- speech-to-text input
- conversational LLM layer
- wake / sleep / stop voice handling
- navigation intent extraction
- coordinated route recording and playback
- Nav2 goal execution in Gazebo
- voice navigation to named pillar locations in the TurtleBot3 simulation world

The main showcase is:

- wake Pepper with voice
- ask Pepper to go to a pillar
- see the intent resolved
- hear the spoken reply
- watch the robot move in simulation

## 2. Main Files

Core runtime files:

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
- `turtlebot_llm_control/llm_intent_test.py`
- `speech_locomotion_interface/speech_locomotion_interface/speech_listener.py`

Packaged demo assets:

- `maps/demo/map.yaml`
- `maps/demo/map.pgm`
- `config/demo_nav2/burger.yaml`
- `config/demo_nav2/waffle.yaml`
- `config/demo_nav2/waffle_pi.yaml`
- `rviz/tb3_navigation2.rviz`

## 3. Build

```bash
cd /home/tom/in_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select turtlebot_llm_control speech_locomotion_interface
source install/setup.bash
```

Set the robot model before launching:

```bash
export TURTLEBOT3_MODEL=waffle
```

`burger` also works if you want to use the burger Nav2 parameters instead.

## 4. LLM Requirements

The default provider is now **Ollama** running locally — no API key required.

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
python3 -m pip install openai
```

To use Groq or OpenAI instead, install the relevant SDK and pass the provider
flags at launch time (see sections 5 and 6).

## 5. Final Demo Launch

Use this for the actual Gazebo showcase:

```bash
cd /home/tom/in_ws
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
- speech-to-text node
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
- that node listens to the shared `/speech/intent` JSON and drives the
  pillar navigation targets directly

Recording flow:

- saying `start recording` enters recording mode
- the recorder opens a separate teleop terminal when a GUI terminal is available
- use `w`, `a`, `s`, `d` to move the robot during the recording session
- press `r` then `Enter` in the teleop terminal to publish the current route label to `/save_tour_command`
- press `esc` in the teleop terminal to stop teleop, end recording, and return the system to autonomy

## 6. Intent-Only Launch

Use this when another workspace owns robot execution, tour playback, waypoint
saving, and locomotion. This launch only runs:

- `speech_to_text_node`
- `speech_command_node`
- optional `speech_debug_node`
- optional `speech_response_node`
- optional tour teleop trigger

It publishes resolved intent JSON to `/speech/intent` by default. It also
publishes the same spoken reply as the standalone tester to `/speech/response`;
set `enable_speech_response:=false` if you want intent publishing only.
With `enable_tour_teleop_trigger:=true`, a `start_recording` intent opens
`tour_teleop_session`. This workspace does not save waypoints; it only starts
teleop, and `tour_teleop_session` publishes the route label on
`/save_tour_command` when you press `r`.

```bash
cd /home/tom/in_ws
source /opt/ros/humble/setup.bash
source /home/tom/turtlebot3_ws/install/setup.bash
source install/setup.bash
ros2 launch turtlebot_llm_control intent_only.launch.py \
  enable_microphone:=true \
  enable_llm:=true \
  llm_provider:=ollama \
  llm_model:=qwen2.5-coder:latest \
  intent_topic:=/speech/intent \
  enable_speech_debug:=true \
  enable_speech_response:=true \
  enable_tour_teleop_trigger:=true \
  energy_threshold:=150 \
  dynamic_energy_threshold:=false \
  calibrate_ambient_noise:=false
```

To test it without the microphone, launch with mock input:

```bash
ros2 launch turtlebot_llm_control intent_only.launch.py \
  enable_microphone:=false \
  intent_topic:=/speech/intent
```

Then publish text:

```bash
ros2 topic pub --once /speech/mock_text std_msgs/msg/String "{data: 'hey pepper go to pillar 3'}"
```

Useful checks:

```bash
ros2 topic echo /speech/intent
ros2 topic echo /speech/response
ros2 topic echo /speech/debug
ros2 topic echo /save_tour_command
```

If a downstream package expects `/intent`, pass `intent_topic:=/intent` instead.

## 7. Standalone Tester

If you want to test speech / LLM behavior without Gazebo:

```bash
cd /home/tom/in_ws
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

If the tester prints `Listening...` but never hears you, first list the
microphones that Python can see:

```bash
ros2 run turtlebot_llm_control llm_intent_test --list-microphones
```

Then run the tester with the matching device index:

```bash
ros2 run turtlebot_llm_control llm_intent_test \
  --provider ollama \
  --model qwen2.5-coder:latest \
  --microphone \
  --mic-device 0
```

If the room is quiet but speech is still not detected, try a lower threshold:

```bash
ros2 run turtlebot_llm_control llm_intent_test \
  --provider ollama \
  --model qwen2.5-coder:latest \
  --microphone \
  --mic-device 0 \
  --energy-threshold 150
```

When `--microphone` is enabled, typed terminal text is ignored. To type test
phrases instead, omit `--microphone`.

## 8. Voice Behavior

Wake phrases:

- `hey pepper`
- `hi pepper`
- `hello pepper`
- `pepper`

After wake-up:

- Pepper stays awake for 45 seconds of inactivity
- each new utterance resets the timer
- if you stay silent long enough, Pepper goes back to sleep

Sleep commands:

- `good night pepper`
- `sleep pepper`
- `pepper sleep`

Emergency stop commands:

- `stop`
- `stop stop`
- `stop now`
- `emergency stop`

These are intended to override whatever the robot is currently doing.

## 9. Demo Commands

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
- `take me to below 1`
- `pepper go to pillar 9`

If the pillar number is missing, Pepper should ask for clarification instead of creating a bad goal.

## 10. Pillar Targets

The demo uses these internal navigation targets:

- `pillar_1`
- `pillar_2`
- `pillar_3`
- `pillar_4`
- `pillar_5`
- `pillar_6`
- `pillar_7`
- `pillar_8`
- `pillar_9`

The speech pipeline normalizes natural variants like:

- `pillar one`
- `Pillar 1`
- `pillow one`
- `below 1`

into the correct internal target.

## 11. Speech And Debug Topics

Main topics:

- `/speech/text`
- `/speech/intent`
- `/speech/response`
- `/speech/debug`
- `/speech_to_text/status`
- `/tour/status`
- `/route/record`
- `/route/data`
- `/save_tour_command`
- `/manual_override/control`

For clean speech-only debugging:

```bash
ros2 topic echo /speech/debug
```

This is the best topic to watch during the demo because it isolates:

- STT status
- recognized text
- resolved intent
- spoken response

If you want to see only the spoken replies:

```bash
ros2 topic echo /speech/response
```

For tour capture and save debugging:

```bash
ros2 topic echo /route/record
ros2 topic echo /route/data
ros2 topic echo /save_tour_command
```

## 12. Notes On TTS

The package uses local desktop TTS tools for audio playback.

Supported commands:

- `spd-say`
- `espeak`
- `say`

If Pepper is not speaking, check:

```bash
which spd-say
which espeak
```

## 13. Known Runtime Noise

You may still see Nav2 / AMCL messages like:

- `Message Filter dropping message`
- TF cache timestamp warnings

These usually happen during startup while Gazebo, TF, localization, and Nav2 are settling.

For this demo, the more important thing is:

- `/speech/debug` shows the right text and intent
- Pepper speaks a response
- the robot accepts the navigation goal and moves

## 14. Quick Checklist

Before the final demo:

1. `colcon build --packages-select turtlebot_llm_control speech_locomotion_interface`
2. `source install/setup.bash`
3. `export TURTLEBOT3_MODEL=waffle`
4. confirm Ollama is running (`curl http://localhost:11434/api/tags`)
5. launch `sim_pillar_nav_demo.launch.py`
6. wait for Gazebo and Nav2 to finish starting
7. keep one terminal on `ros2 topic echo /speech/debug`

## 15. One-Line Demo Reminder

```text
hey pepper -> go to pillar one -> Pepper answers -> intent resolves -> robot navigates
```
