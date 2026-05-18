# ARIA Social Tour Guide Robot — User Guide

## What is this robot?

ARIA is a social tour guide robot built on TurtleBot3. She can autonomously guide visitors through pre-recorded tours, answer questions about locations, and respond to natural voice commands. ARIA uses an offline AI brain powered by Qwen2.5, which means she works reliably in any venue without needing an internet connection.

ARIA remembers previous conversations across sessions — so if a visitor has a favourite nickname for a location, she will remember it next time. She can also be paused mid-tour, answer a visitor question, and then continue exactly where she left off.

---

## Quick Start

1. Power on the robot and make sure the computer running ROS2 is connected to the same network.
2. Open a terminal and start the social guide navigation stack:
   ```
   ros2 launch turtlebot_social_guide tour_manager_launch.py
   ```
3. Open a second terminal and start the LLM speech system:
   ```
   ros2 launch turtlebot_llm_control bringup.launch.py
   ```
4. Say **"Hey ARIA"** to wake the robot. You will hear/see a confirmation.
5. Give a command — for example: **"Start tour one"**.

> **Tip:** If ARIA does not respond, check that Ollama is running (`ollama serve` in a terminal).

---

## Voice Commands

| What you say | What happens |
|---|---|
| "Hey ARIA" or "Hey pepper" | Wakes the robot — it will now listen for commands for 45 seconds |
| "Are you there?" / "Can you hear me?" | ARIA confirms she is active |
| **"Start tour one"** | Begins the tour named `tour1` — robot visits each saved stop in order |
| **"Start tour two"** | Begins `tour2` |
| "Begin the guided tour" | Same as start tour one |
| "Go to waypoint three" | Navigates directly to saved waypoint number 3 |
| "Take me to the entrance" | Navigates to wherever "entrance" was described |
| "Tell me about this place" | ARIA describes the current location |
| "What is this?" | Same as above |
| "Follow me" | ARIA follows the speaker around |
| **"Stop"** | Stops all movement immediately |
| "Stop navigation" | Cancels current navigation but keeps ARIA awake |
| **"Pause"** | Pauses current tour (ARIA stops in place, remembers position) |
| **"Resume"** | Continues from where ARIA paused |
| "Go home" / "Return to dock" | Robot navigates back to its charging station |

> ARIA also understands naturally phrased requests. For example, "take me to the paintings area" will work even if the waypoint is saved as "art_gallery" — ARIA is smart enough to make the connection.

---

## Recording a New Location (Step by Step)

Use this when you want to add a new stop that ARIA can navigate to or include in a tour.

**What you need:** The social guide nodes running, and a keyboard teleop in a separate terminal.

1. Open a terminal and start the waypoint recorder:
   ```
   ros2 run tour_maker waypoint_recorder
   ```
2. Open another terminal and start keyboard teleoperation:
   ```
   ros2 run teleop_twist_keyboard teleop_twist_keyboard
   ```
3. Use the keyboard teleop to drive the robot to the location you want to save.
4. Switch to the **waypoint recorder terminal** and press **R**, then **Enter**.
5. You will see a confirmation: `✓ Waypoint #1 saved at (x, y)`.
6. Drive to the next location and press R + Enter again. Repeat for all locations.
7. Press **Q + Enter** to quit the waypoint recorder when done.

All saved waypoints are stored automatically in the social guide database and will appear the next time you run the Tour Planner.

---

## Planning a Tour (Step by Step)

Use this after you have saved at least two waypoints.

1. Open a terminal and run:
   ```
   ros2 run tour_maker tour_planner
   ```
2. A map window opens showing your environment with **numbered red dots** — one for each saved waypoint.
3. In the terminal, type the waypoint numbers in the order you want the tour to visit them, separated by spaces.
   - Example: `3 1 7 2 5` — visits stop 3 first, then 1, then 7, then 2, then 5.
4. For each stop, you can type what ARIA should say when she arrives (press Enter to skip for a silent stop).
   - Example: *"Welcome to the main gallery! This collection was established in 1923."*
5. Give the tour a name when prompted — for example `tour1` or `entrance_gallery`.
6. The tour CSV file is saved automatically to `~/tours/`.

To start this tour, simply say: **"Start tour [name]"**

---

## Features at a Glance

- **Offline AI brain** — works in any venue without internet, powered by Qwen2.5 running locally
- **Memory across sessions** — ARIA remembers previous conversations, learned nicknames for locations, and facts about visitors
- **Fuzzy understanding** — say "take me to the paintings area" even if the waypoint is called "art_gallery" — ARIA figures it out
- **Artifact descriptions** — ARIA speaks a custom description when she arrives at each tour stop
- **Pause and resume** — stop mid-tour to answer a question, then pick up exactly where you left off
- **Multiple tours** — create and name as many tours as you like (`tour1`, `tour2`, `entrance_gallery`, etc.)
- **Expression feedback** — ARIA signals her current state (thinking, navigating, explaining) for visual displays
- **Emergency stop** — say "stop" or "emergency stop" at any time to halt immediately

---

## Common Problems and Fixes

| What you see or hear | Likely cause | What to do |
|---|---|---|
| "I'm thinking in basic mode right now" | Ollama AI service not running | Open a terminal and run: `ollama serve` |
| ARIA does not respond at all | Wake word not detected | Say "Hey ARIA" clearly first, then your command |
| "I couldn't find tour 1" | Tour CSV file not created yet | Run `ros2 run tour_maker tour_planner` to create it |
| Robot stops mid-tour unexpectedly | Navigation obstacle blocked the path | Say "resume" to retry, or "stop" to cancel |
| Waypoints not showing in Tour Planner | Social guide nodes not running | Launch `turtlebot_social_guide tour_manager_launch.py` first |
| "tour_retrieve service not available" | Social guide nodes not launched | Start the social guide stack before the tour planner |
| ARIA mishears a command | Background noise too high | Speak closer to the microphone, or use mock text for testing |
| Map window does not open | matplotlib not installed | Run: `pip install matplotlib numpy` |
