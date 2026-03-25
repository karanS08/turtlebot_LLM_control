# TurtleBot LLM Control

## Academic Context

This repository is part of the **Social Tour Guide Robot** project developed at the **University of Technology Sydney (UTS)** within:

- **Faculty of Engineering and IT**
- **School of Mechanical and Mechatronic Engineering**
- **41069 Robotics Studio 2**

The broader project goal was to develop a socially interactive robot capable of guiding visitors through an environment while combining autonomous navigation with natural human-robot interaction.

This repository represents the subsystem work for the **human-machine interface and behavior** portion of that project. In the team contract, this subsystem was led by **Karan Sharma** with responsibility for:

- speech-to-text integration and command recognition
- command-to-action mapping for high-level robot behaviors
- triggering navigation goals through ROS2
- verbal responses to recognized commands
- behavior-tree-oriented control logic for navigation start and stop

## Background

This project explores a simple but practical question: how do we make a mobile robot feel easier and more natural to interact with using speech?

The final demo focuses on a TurtleBot3 in Gazebo that can be woken by voice, understand everyday spoken requests, convert them into robot intents, and execute navigation through ROS2 and Nav2. Instead of treating speech as a fixed button press replacement, the system combines speech recognition, intent parsing, wake-word handling, a conversational LLM layer, and a lightweight behavior orchestration flow so the robot can both chat and act.

The goal of this phase was to build a clean end-to-end voice navigation demo, not a full general-purpose robot assistant. The result is a package that is small enough to understand, focused enough to demonstrate clearly, and practical enough to extend in later phases.

## Contribution And Ownership

This repository highlights Karan Sharma's contribution to the project as the developer responsible for the behavior and speech interaction layer that connects user language to robot action.

The work in this repository focused on building the layer that makes the robot usable from a human perspective:

- interpreting spoken language as actionable intent
- deciding when an utterance is a command versus normal conversation
- translating navigation requests into structured robot targets
- coordinating wake, sleep, interruption, and stop behavior
- linking speech interaction to ROS2 navigation execution

Within the overall Social Tour Guide Robot project, this was a central integration point because it connected the user-facing interaction loop to the robot's motion and decision-making pipeline. In practical terms, this is the layer that allows a person to speak naturally to the robot and receive an understandable, observable robotic response.

While the full project was team-based, this subsystem contributed a large share of the interaction quality visible in the final demo because it was responsible for how commands were understood, how actions were triggered, and how the robot communicated back to the user.

## What This Demo Achieves

The final demo shows that a spoken request can move through the full stack:

- the robot listens for a wake phrase such as `hey pepper`
- speech is transcribed into text
- the text is interpreted as either conversation or robot intent
- navigation commands like `go to pillar 5` are normalized into internal targets
- the behavior layer sends a Nav2 goal through ROS2
- the robot responds verbally and starts moving in Gazebo

This demo also includes a more human-friendly interaction loop around that core pipeline:

- Pepper stays awake for a short inactivity window after wake-up
- casual conversation can be handled without forcing every utterance into a robot command
- `sleep pepper` and `good night pepper` return the robot to a non-listening state
- `stop`, `stop stop`, and `emergency stop` are treated as high-priority overrides

## Why It Helps

This kind of system helps bridge the gap between traditional robotics interfaces and natural human interaction.

It can help with:

- making robot control more accessible for non-technical users
- reducing the need for manual teleoperation or UI-driven goal selection
- demonstrating how LLMs can complement classical ROS2 pipelines instead of replacing them
- turning noisy, natural spoken language into structured robot actions
- creating a better foundation for future assistive, tour-guide, and human-robot interaction applications

## Final Demo Scenario

The package is now centered on one purpose-driven showcase:

1. Launch a TurtleBot3 simulation in Gazebo.
2. Bring up localization, navigation, speech, and orchestration nodes.
3. Wake Pepper by voice.
4. Ask Pepper to go to one of nine named pillar locations.
5. Watch the robot acknowledge the request and navigate to that target.

Typical demo phrases include:

- `hey pepper`
- `go to pillar 1`
- `take me to pillar five`
- `pepper go to pillar 9`
- `stop`

The speech pipeline also handles common transcription drift such as `pillow one` when the intended destination is `pillar 1`.

## Main Features

- Voice wake, sleep, and inactivity-based listening control
- Speech-to-text integration for live microphone input
- Intent extraction for navigation and control actions
- Conversational LLM fallback for non-command speech
- Verbal responses through the speaker node
- Nav2 goal execution in simulation
- Nine predefined pillar destinations for a clear navigation demo
- Isolated speech debug output for easier live troubleshooting

## Technologies Used

The final demo combines the following tools and frameworks:

- ROS2 Humble
- Python
- TurtleBot3 simulation
- Gazebo
- Nav2
- RViz2
- `speech_recognition` for speech-to-text
- Groq or OpenAI-backed LLM integration
- Linux text-to-speech tools such as `spd-say` / `espeak`

The design intentionally mixes classical robotics components with an LLM-based language layer. ROS2 topics, actions, and behavior coordination remain responsible for robot execution, while the LLM is used to make user language more flexible and conversational.

## Architecture At A Glance

The main runtime path is:

`speech_to_text_node` -> `speech_command_node` -> `bt_orchestrator_node`

Supporting modules provide:

- wake-word and sleep-state handling
- speech parsing and intent normalization
- LLM-backed dialogue and intent fallback
- spoken responses
- debug aggregation
- initial pose setup for simulation

The main packaged demo launch is:

- [sim_pillar_nav_demo.launch.py](/home/karan/ros2_ws/src/turtlebot_llm_control/launch/sim_pillar_nav_demo.launch.py)

## What Was Learned Along The Way

This project surfaced a number of practical lessons that are easy to miss in a purely conceptual design.

- Speech recognition is noisy in real use, so the system needed tolerance for misheard phrases like `pillow one`, missing words, and shuffled wording.
- Wake-word handling matters a lot for user experience. A robot that is always listening can feel messy, but a robot that sleeps too aggressively becomes frustrating.
- Stop behavior must be treated as a real override, not just another command in queue. Otherwise the robot can finish an older goal before stopping.
- LLM output still needs structure and guardrails. Natural language flexibility is helpful, but the robot side needs normalized intent tokens such as `pillar_1`.
- Good demos depend on debugging visibility. Separating speech-related logs from general ROS navigation noise made the system much easier to validate live.
- Packaging the maps, Nav2 config, and launch files inside the package made the demo more reproducible and GitHub-ready.

## What Was Achieved In This Phase

By the end of this phase, the project achieved:

- speech-to-text integration with command recognition
- basic command-to-action mapping for navigation and control
- ROS2-triggered navigation goals through Nav2
- verbal responses for recognized commands
- a lightweight behavior-tree-style orchestration path for navigation start and stop
- a complete simulation demo where Pepper can be asked to navigate to named pillars by voice

These outcomes directly align with the contracted **P-level** goals for Subsystem 3 and extend toward the project's higher-level objective of converting spoken input into structured actions interpretable by the robot control framework.

## Repository Focus

This repository has been cleaned to support the final demo directly. Older experimental files for bin missions, reactive tests, and unrelated launch flows were removed so the package stays focused on the final showcase.

The most important files for this demo are:

- [GUIDE.md](/home/karan/ros2_ws/src/turtlebot_llm_control/GUIDE.md)
- [launch/sim_pillar_nav_demo.launch.py](/home/karan/ros2_ws/src/turtlebot_llm_control/launch/sim_pillar_nav_demo.launch.py)
- [launch/bringup.launch.py](/home/karan/ros2_ws/src/turtlebot_llm_control/launch/bringup.launch.py)
- [turtlebot_llm_control/speech_to_text_node.py](/home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/speech_to_text_node.py)
- [turtlebot_llm_control/speech_command_node.py](/home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/speech_command_node.py)
- [turtlebot_llm_control/bt_orchestrator_node.py](/home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/bt_orchestrator_node.py)
- [turtlebot_llm_control/llm_dialogue.py](/home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/llm_dialogue.py)
- [turtlebot_llm_control/speech_parser.py](/home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/speech_parser.py)

## Running The Demo

The detailed setup and commands are documented in [GUIDE.md](/home/karan/ros2_ws/src/turtlebot_llm_control/GUIDE.md).

In short:

```bash
cd /home/karan/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select turtlebot_llm_control
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

For a speech-only tester without Gazebo:

```bash
ros2 run turtlebot_llm_control llm_intent_test \
  --provider groq \
  --model llama-3.3-70b-versatile \
  --key /home/karan/ros2_ws/src/turtlebot_llm_control/turtlebot_llm_control/api.key \
  --microphone
```

## Future Direction

This phase intentionally stops at a clean, explainable voice-navigation demo. The next logical extensions would be richer memory, live world knowledge, stronger dialogue continuity, and more real robot behaviors, but those are beyond the scope of this final submission.

## Professional Summary

From an engineering perspective, this repository demonstrates practical experience in:

- ROS2 system integration
- speech-driven robot interaction design
- intent parsing and LLM-assisted command understanding
- Nav2 goal orchestration
- simulation-first robotics development
- debugging and packaging a reproducible demo for delivery
