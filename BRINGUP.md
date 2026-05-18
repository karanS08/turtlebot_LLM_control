# ARIA Social Tour Guide Robot — Bringup Guide

This guide walks through bringing up the full system in order, starting with Gazebo simulation so everything can be tested on your laptop before touching physical hardware.

Each step is a separate terminal. Keep them all open — they all need to stay running.

---

## Prerequisites (one-time setup)

```bash
# 1. Install pip dependencies
pip install faster-whisper sounddevice numpy matplotlib

# 2. Pull the Ollama LLM model (downloads ~4 GB, one time only)
ollama pull qwen2.5

# 3. Build the workspace
cd ~/social_ws
source /opt/ros/humble/setup.bash
source src/turtlebot_social_guide/install/setup.bash
colcon build --packages-select turtlebot_llm_control
source install/setup.bash
```

---

## Part A — Simulation (No Robot Required)

Run these steps in order. Each is a new terminal window.

---

### Terminal 1 — Ollama LLM Server

```bash
ollama serve
```

Leave running. Verify it works:

```bash
curl http://localhost:11434/api/tags
# Should return JSON listing available models
```

---

### Terminal 2 — Gazebo Simulation (TurtleBot3)

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

A Gazebo window opens showing the robot in a test world. Wait until you see the robot appear before proceeding.

> **Tip:** If you have a pre-built map from a previous session, skip to Terminal 3. If not, use cartographer to build one now (see the mapping section below), then come back here.

---

### Terminal 3 — Nav2 Navigation Stack

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=True \
  map:=$HOME/maps/my_map.yaml
```

Replace `my_map.yaml` with your actual map file. An RViz window opens showing the map and the robot's estimated position.

**Set the initial pose in RViz:**
1. Click the **2D Pose Estimate** button in RViz.
2. Click on the map where the robot is in Gazebo and drag to set the heading.
3. Wait for the particle cloud to converge (white dots cluster around the robot).

---

### Terminal 4 — Social Guide Stack

```bash
source /opt/ros/humble/setup.bash
source ~/social_ws/install/setup.bash
ros2 launch tour_manager tour_manager_launch.py
```

This starts the waypoint database and tour execution services used by the LLM system.

Confirm it's running:

```bash
ros2 service list | grep tour
# Should show: /tour_retrieve
```

---

### Terminal 5 — LLM Control Stack

```bash
source /opt/ros/humble/setup.bash
source ~/social_ws/install/setup.bash
ros2 launch turtlebot_llm_control bringup.launch.py \
  enable_microphone:=true \
  hardware:=false
```

Key flags for simulation:
| Flag | Simulation value | Real robot value |
|------|-----------------|------------------|
| `hardware` | `false` | `true` |
| `enable_microphone` | `false` | `true` |
| `enable_llm` | `true` | `true` |
| `whisper_model` | `base` | `base` or `small` |
| `mute` | `false` | `false` |

---

### Terminal 6 — Debug Monitor (Voice Message Viewer)

```bash
source /opt/ros/humble/setup.bash
source ~/social_ws/install/setup.bash
ros2 topic echo /speech/debug
```

This prints every step of the voice pipeline in real time:

```
[stt_status]  Listening for wake word…
[heard]       start tour one
[intent]      intent=start_tour label=1 conf=0.95
[ARIA]        "Starting tour 1 — let's go!"
```

The debug node also prints colour-coded output directly in Terminal 5. You can watch either.

---

### Terminal 7 — Inject Test Commands (Mock Voice)

Since `enable_microphone:=false`, commands come from this topic instead of a real microphone:

```bash
source /opt/ros/humble/setup.bash

# Wake the robot first (required if require_wake_word:=true)
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'hey aria'"

# Then send a command
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'go to waypoint 0'"
```

**Useful test commands:**

```bash
# Check if the robot is alive
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'hey aria are you there'"

# Navigate to a waypoint (must have saved waypoints first)
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'hey aria go to waypoint 2'"

# Start a tour (must have a tour CSV in ~/tours/)
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'hey aria start tour one'"

# Pause and resume
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'hey aria pause'"
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'hey aria resume'"

# Emergency stop
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'hey aria stop'"
```

**Watch what the robot hears and does:**

```bash
# In separate terminals — run any of these for more detail
ros2 topic echo /speech/text        # What STT heard (post wake-word gate)
ros2 topic echo /speech/intent      # Intent JSON from LLM brain
ros2 topic echo /speech/response    # Text the robot speaks
ros2 topic echo /robot/expression   # Current robot state (THINKING, NAVIGATING, etc.)
ros2 topic echo /tour/status        # Full BT status including active tour, waypoints
```

---

## Part B — Building a Map (First Time Only)

If you do not have a map yet, use SLAM to build one in Gazebo before running Nav2.

### Terminal 2b — Cartographer SLAM (instead of Nav2)

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

### Terminal 3b — Keyboard Teleop to Drive the Robot

```bash
source /opt/ros/humble/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Drive the robot around the full environment. Watch the map build in the RViz window.

### Save the map

```bash
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map
```

This creates `~/maps/my_map.yaml` and `~/maps/my_map.pgm`. Now restart with Nav2 (Terminal 3 above).

---

## Part C — Recording Waypoints in Simulation

After the map is built and Nav2 is running:

### Terminal 8 — Waypoint Recorder

```bash
source /opt/ros/humble/setup.bash
source ~/social_ws/install/setup.bash
ros2 run turtlebot_llm_control waypoint_recorder
```

### Terminal 3b (reuse) — Keyboard Teleop

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Drive the robot to a location of interest in Gazebo. Switch to the waypoint recorder terminal and press **R + Enter** to save it. Repeat for each location. Press **Q + Enter** when done.

### Terminal 9 — Tour Planner

```bash
source /opt/ros/humble/setup.bash
source ~/social_ws/install/setup.bash
ros2 run turtlebot_llm_control tour_planner
```

A matplotlib window shows the map with numbered waypoints. Follow the prompts to build a tour CSV.

---

## Part D — Real Robot (After Simulation Testing)

The steps are identical to simulation — only the launch flags change.

### Terminal 1 — Ollama (same as simulation)

```bash
ollama serve
```

### Terminal 2 — TurtleBot3 Bringup (replaces Gazebo)

On the **robot's PC** (SSH in):

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_bringup robot.launch.py
```

### Terminal 3 — Nav2 with Pre-Built Map

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=False \
  map:=$HOME/maps/my_map.yaml
```

Set the initial pose in RViz as before.

### Terminal 4 — Social Guide Stack (same as simulation)

```bash
source /opt/ros/humble/setup.bash
source ~/social_ws/install/setup.bash
ros2 launch tour_manager tour_manager_launch.py
```

### Terminal 5 — LLM Control Stack (with microphone + hardware flags)

```bash
source ~/social_ws/install/setup.bash
ros2 launch turtlebot_llm_control bringup.launch.py \
  hardware:=true \
  enable_microphone:=true \
  whisper_model:=base
```

Say **"Hey ARIA"** and wait for the listening confirmation. Then give a command.

---

## Quick Reference — All Topics

| Topic | What it shows |
|-------|--------------|
| `/speech/mock_text` | Inject commands without a microphone |
| `/speech/text` | What the STT heard after wake-word gate |
| `/speech/intent` | Intent JSON parsed by the LLM brain |
| `/speech/response` | Text ARIA is about to speak |
| `/robot/expression` | Robot state: THINKING / TALKING / NAVIGATING / etc. |
| `/speech/debug` | All of the above in one stream (use for rosbag) |
| `/tour/status` | Full BT state: current tour, waypoint index, available tours |
| `/follow_me/control` | Follow-me subsystem control |
| `/save_tour_command` | Triggers waypoint save (published by waypoint_recorder) |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `[ARIA] "I'm thinking in basic mode"` | Ollama not running | Run `ollama serve` in Terminal 1 |
| `[ARIA] "I couldn't find tour 1"` | No tour CSV exists | Run `tour_planner` to create one |
| `/speech/debug` shows nothing | Speech debug node not running | It is enabled by default; check Terminal 5 logs |
| Nav2 goal rejected | Robot not localised | Re-set 2D Pose Estimate in RViz |
| `tour_retrieve` service missing | Social guide not running | Start Terminal 4 first |
| Mock text ignored | Wake word not sent yet | Send `"hey aria"` first, then the command |
| Gazebo robot does not move | Nav2 not started | Nav2 must be running (Terminal 3) |
| Map not loading | Wrong path | Check `ls ~/maps/my_map.yaml` exists |
