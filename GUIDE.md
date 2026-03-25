# TurtleBot LLM Control Demo Guide

## 1. Purpose

This package is now focused on one final demo:

- speech-to-text input
- conversational LLM layer
- wake / sleep / stop voice handling
- navigation intent extraction
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
- `turtlebot_llm_control/llm_dialogue.py`
- `turtlebot_llm_control/speech_parser.py`
- `turtlebot_llm_control/wake_word.py`
- `turtlebot_llm_control/llm_intent_test.py`

Packaged demo assets:

- `maps/demo/map.yaml`
- `maps/demo/map.pgm`
- `config/demo_nav2/burger.yaml`
- `config/demo_nav2/waffle.yaml`
- `config/demo_nav2/waffle_pi.yaml`
- `rviz/tb3_navigation2.rviz`

## 3. Build

```bash
cd /home/karan/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select turtlebot_llm_control
source install/setup.bash
```

Set the robot model before launching:

```bash
export TURTLEBOT3_MODEL=waffle
```

`burger` also works if you want to use the burger Nav2 parameters instead.

## 4. LLM Requirements

For Groq:

- install the SDK:

```bash
python3 -m pip install groq
```

- either export the key:

```bash
export GROQ_API_KEY=your_key_here
```

- or create a local untracked file beside `api.key.example`:

```bash
cp src/turtlebot_llm_control/turtlebot_llm_control/api.key.example \
   src/turtlebot_llm_control/turtlebot_llm_control/api.key
```

Then paste your real key into `src/turtlebot_llm_control/turtlebot_llm_control/api.key`.

That file is ignored by Git.

## 5. Final Demo Launch

Use this for the actual Gazebo showcase:

```bash
cd /home/karan/ros2_ws
source install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot_llm_control sim_pillar_nav_demo.launch.py \
  enable_microphone:=true \
  enable_llm:=true \
  llm_provider:=groq \
  llm_model:=llama-3.3-70b-versatile \
  llm_api_key_path:=/home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/api.key \
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
- follow node
- initial pose publisher for the simulated robot

## 6. Standalone Tester

If you want to test speech / LLM behavior without Gazebo:

```bash
cd /home/karan/ros2_ws
source install/setup.bash
ros2 run turtlebot_llm_control llm_intent_test \
  --provider groq \
  --model llama-3.3-70b-versatile \
  --key /home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/api.key \
  --microphone
```

Useful flags:

- `--mute`
- `--no-llm`
- `--wake-timeout 45.0`

## 7. Voice Behavior

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

## 8. Demo Commands

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

## 9. Pillar Targets

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

## 10. Speech And Debug Topics

Main topics:

- `/speech/text`
- `/speech/intent`
- `/speech/response`
- `/speech/debug`
- `/speech_to_text/status`
- `/tour/status`

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

## 11. Notes On TTS

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

## 12. Known Runtime Noise

You may still see Nav2 / AMCL messages like:

- `Message Filter dropping message`
- TF cache timestamp warnings

These usually happen during startup while Gazebo, TF, localization, and Nav2 are settling.

For this demo, the more important thing is:

- `/speech/debug` shows the right text and intent
- Pepper speaks a response
- the robot accepts the navigation goal and moves

## 13. Quick Checklist

Before the final demo:

1. `colcon build --packages-select turtlebot_llm_control`
2. `source install/setup.bash`
3. `export TURTLEBOT3_MODEL=waffle`
4. confirm your Groq key is available
5. launch `sim_pillar_nav_demo.launch.py`
6. wait for Gazebo and Nav2 to finish starting
7. keep one terminal on `ros2 topic echo /speech/debug`

## 14. One-Line Demo Reminder

```text
hey pepper -> go to pillar one -> Pepper answers -> intent resolves -> robot navigates
```
