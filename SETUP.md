# TurtleBot LLM Social Tour Guide — Setup Guide

> **What this guide covers:** Everything needed to go from a clean Ubuntu 22.04
> machine to a fully running social tour-guide robot — simulation or real
> hardware.  Follow the sections in order the first time.

---

## Before You Start

**What you are setting up**

A ROS 2 robot that:
- navigates autonomously using Nav2
- listens to voice commands via a microphone
- classifies intent using a fully-offline Qwen LLM (no internet required)
- guides visitors on tours, explaining each stop from a knowledge database
- answers visitor questions using Retrieval-Augmented Generation (RAG)

**Time estimate**

| Section | Time (first run) |
|---|---|
| ROS 2 Humble | 10–20 min (download) |
| TurtleBot 3 + Nav2 + Gazebo | 5–10 min |
| Ollama + Qwen model | 10–20 min (4.7 GB download) |
| Workspace build | 2–5 min |
| Total | ~30–55 min |

**Requirements**

| | Minimum | Recommended |
|---|---|---|
| OS | Ubuntu 22.04 LTS (x86-64) | Ubuntu 22.04 LTS (x86-64) |
| CPU | 4-core | 8-core |
| RAM | 8 GB | 16 GB |
| Disk | 20 GB free | 40 GB free |
| GPU | Not required | NVIDIA 6 GB VRAM (faster LLM) |
| Microphone | Not required | USB cardioid mic |

> **Note:** ROS 2 Humble has very limited support outside Ubuntu 22.04 x86-64.
> If you are on another platform, use a native Ubuntu 22.04 VM.

---

## Step 1 — Base System Packages

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
  build-essential cmake git curl wget \
  python3-pip python3-venv \
  python3-tk \
  portaudio19-dev \
  libssl-dev lsb-release gnupg2 \
  software-properties-common
```

`python3-tk` — required for the knowledge editor GUI  
`portaudio19-dev` — required for microphone input

---

## Step 2 — ROS 2 Humble

### Add the apt repository

```bash
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu \
  $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
```

### Install

```bash
sudo apt install -y ros-humble-desktop-full
sudo apt install -y python3-colcon-common-extensions python3-rosdep
```

### Initialise rosdep

```bash
sudo rosdep init
rosdep update
```

### Add to your shell

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Verify

```bash
ros2 --version
# Expected: ros2 cli version X.X.X
```

---

## Step 3 — TurtleBot 3

### Install packages

```bash
sudo apt install -y \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-msgs \
  ros-humble-turtlebot3-simulations \
  ros-humble-turtlebot3-gazebo \
  ros-humble-turtlebot3-bringup
```

### Set your robot model

```bash
echo "export TURTLEBOT3_MODEL=waffle" >> ~/.bashrc
source ~/.bashrc
```

| Value | Use when |
|---|---|
| `burger` | You have a physical Burger robot |
| `waffle` | Simulation, or you have a physical Waffle |
| `waffle_pi` | You have a physical Waffle Pi |

### Verify

```bash
ros2 pkg list | grep turtlebot3
# Should list: turtlebot3, turtlebot3_gazebo, turtlebot3_msgs, ...
```

---

## Step 4 — Nav2 Navigation Stack

Nav2 provides localisation (AMCL), path planning, and motion control.

```bash
sudo apt install -y \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-nav2-simple-commander \
  ros-humble-nav2-msgs \
  ros-humble-tf-transformations
```

---

## Step 5 — Gazebo Simulation

```bash
sudo apt install -y \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros2-control
```

### Verify

```bash
gazebo --version
# Expected: Gazebo multi-robot simulator, version 11.x.x
```

---

## Step 6 — Ollama (Offline LLM)

All language model inference runs **locally** through Ollama.  
No API keys, no internet connection, no cloud account required.

### 6.1 Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 6.2 Start the server

Ollama needs to be running in a terminal before any ROS nodes start.

```bash
ollama serve
```

The server listens on `http://localhost:11434`.  Leave this terminal open.

### 6.3 Download the model

In a **second terminal**:

```bash
ollama pull qwen2.5:7b
```

This downloads ~4.7 GB once.  All future starts are instant.

**Choose a model based on your hardware:**

| Model | Download size | RAM needed | When to use |
|---|---|---|---|
| `qwen2.5:3b` | ~2 GB | 4 GB | Low-memory machines, fastest responses |
| `qwen2.5:7b` | ~4.7 GB | 8 GB | **Default — best balance** |
| `qwen2.5:14b` | ~9 GB | 16 GB | Higher quality reasoning |

To use a different model, add `llm_model:=qwen2.5:3b` when launching.

### 6.4 Install the Python client

```bash
pip install ollama
```

### 6.5 Verify the full chain

```bash
ollama run qwen2.5:7b "Say hello in one sentence."
# The model should respond with a single sentence.
# Press Ctrl+D or type /bye to exit.
```

---

## Step 7 — Speech and Audio

### Text-to-speech (robot voice output)

```bash
sudo apt install -y speech-dispatcher espeak
```

Test:

```bash
spd-say "Hello, I am your tour guide."
```

If no sound plays, check your audio device:

```bash
pactl list sinks short
```

### Speech recognition (microphone input)

```bash
pip install SpeechRecognition PyAudio
```

If PyAudio fails to install via pip:

```bash
sudo apt install -y python3-pyaudio
```

List available microphones:

```bash
python3 -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

> **No microphone?** You can inject commands as text over ROS topics — see
> [Section 10.3 — Testing without a microphone](#103-testing-without-a-microphone).

---

## Step 8 — Python Packages

```bash
pip install \
  ollama \
  SpeechRecognition \
  PyAudio \
  opencv-python \
  transforms3d
```

| Package | Purpose |
|---|---|
| `ollama` | Offline LLM inference |
| `SpeechRecognition` | Microphone audio → text |
| `PyAudio` | Microphone access backend |
| `opencv-python` | Colour tracking for follow-me mode |
| `transforms3d` | Quaternion utilities |

---

## Step 9 — Build the Workspace

### 9.1 Navigate to the workspace

```bash
cd /home/karan/in_ws
```

### 9.2 Resolve ROS dependencies

```bash
rosdep install --from-paths src --ignore-src -r -y
```

This reads every `package.xml` in `src/` and installs any missing apt packages.

### 9.3 Build

```bash
colcon build
```

To rebuild only the project packages (faster after the first full build):

```bash
colcon build --packages-select \
  turtlebot_llm_control \
  social_robot_interfaces \
  speech_locomotion_interface \
  tour_manager \
  robot_tour
```

### 9.4 Source the overlay

Run this in **every new terminal** before using `ros2 run` or `ros2 launch`:

```bash
source /home/karan/in_ws/install/setup.bash
```

Add it permanently so you never forget:

```bash
echo "source /home/karan/in_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 9.5 Verify

```bash
ros2 pkg list | grep turtlebot_llm
# Expected: turtlebot_llm_control
```

---

## Step 10 — Run the Simulation Demo

Open **four terminals**.  Each one should have the workspace sourced.

---

### Terminal 1 — Ollama server

```bash
ollama serve
```

Keep running for the whole session.

---

### Terminal 2 — Simulation launch

```bash
cd /home/karan/in_ws
source install/setup.bash
export TURTLEBOT3_MODEL=waffle

ros2 launch turtlebot_llm_control sim_pillar_nav_demo.launch.py \
  enable_microphone:=true \
  llm_model:=qwen2.5:7b \
  mute:=false
```

**What to wait for (takes 30–60 seconds):**

1. Gazebo window opens — robot spawns at position (−2.0, −0.5)
2. RViz window opens — map loads with the pillar arena
3. Terminal prints `Nav2 is ready`
4. Terminal prints `Behavior-tree orchestrator ready`

---

### Terminal 3 — Monitor the speech pipeline

```bash
source /home/karan/in_ws/install/setup.bash
ros2 topic echo /speech/debug
```

Every spoken command, parsed intent, and robot response will appear here.

---

### 10.3 Testing without a microphone

Use Terminal 4 to inject text commands directly:

```bash
source /home/karan/in_ws/install/setup.bash

# Wake the robot (activates the wake-word gate)
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'hey pepper'"

# Navigate to a location
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'go to pillar 1'"

# Start a guided tour
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'start tour'"

# Ask a knowledge question
ros2 topic pub --once /speech/mock_text std_msgs/String "data: 'what is in this room'"
```

Watch Terminal 3 to trace each step through the pipeline.

---

## Step 11 — Knowledge Editor

The knowledge editor lets you attach information to map locations.  When the
robot arrives at a waypoint during a tour, it reads the attached text aloud.
Visitor questions are answered by searching all entries (RAG).

### Open the editor

```bash
ros2 run turtlebot_llm_control knowledge_editor
```

The database is stored at:

```
~/.local/share/turtlebot_llm_control/knowledge.db
```

It is created automatically on first launch.

### Creating an entry

| Field | What to enter |
|---|---|
| **Key** | Unique slug, no spaces — e.g. `library`, `main_hall` |
| **Title** | Human-readable name — e.g. `The Main Library` |
| **Kind** | `place` for physical tour stops |
| **X / Y** | Map coordinates (see below) |
| **Yaw** | Robot facing direction in radians (0 = East, 1.57 = North) |
| **Arrival Speech** | Exact text the robot speaks on arrival.  Leave blank to auto-generate. |
| **Wiki / Notes** | Full background text used for RAG question answering. |

Click **Save Entry** when done.

### Getting map coordinates

While the simulation is running, drive the robot to the desired location and read its pose:

```bash
ros2 topic echo /amcl_pose --once
# Read: pose.pose.position.x and pose.pose.position.y
```

Or click a point in RViz — the coordinates appear in the bottom status bar.

### Preview arrival speech before a tour

1. Select an entry in the list.
2. Click **Preview Arrival Speech**.
3. A popup shows exactly what the robot will say at that stop.

### Test RAG answers

1. Type a visitor question in the **Ask a Question** box, e.g. `What is special about this room?`
2. Click **Ask**.
3. Ollama searches the knowledge database and returns a grounded answer.

The status bar shows `Ollama ready (model: qwen2.5:7b)` when the LLM is connected.

---

## Step 12 — Real Hardware Deployment

### On the TurtleBot (Raspberry Pi)

SSH into the robot:

```bash
ssh ubuntu@<ROBOT_IP>
```

On the robot:

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger   # or waffle / waffle_pi
ros2 launch turtlebot3_bringup robot.launch.py
```

### On your workstation — Nav2

```bash
export ROS_DOMAIN_ID=0           # must match the robot
source /opt/ros/humble/setup.bash
source /home/karan/in_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger

ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  map:=/home/karan/in_ws/src/turtlebot_LLM_control/maps/demo/map.yaml \
  use_sim_time:=false
```

### On your workstation — LLM control stack

```bash
ros2 launch turtlebot_llm_control bringup.launch.py \
  hardware:=true \
  enable_microphone:=true \
  llm_model:=qwen2.5:7b \
  ollama_host:=http://localhost:11434
```

### Network requirement

Both the robot and workstation must be on the **same Wi-Fi network** with
matching `ROS_DOMAIN_ID`.  Verify topic visibility from the workstation:

```bash
ros2 topic list
# Should show /scan, /odom, /cmd_vel from the robot
```

---

## Step 13 — Environment Variables

Add all of these to `~/.bashrc` once:

```bash
# ROS 2 Humble
source /opt/ros/humble/setup.bash

# Project workspace overlay
source /home/karan/in_ws/install/setup.bash

# TurtleBot model (waffle / burger / waffle_pi)
export TURTLEBOT3_MODEL=waffle

# Gazebo model path for TurtleBot 3
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models
```

Apply:

```bash
source ~/.bashrc
```

---

## Step 14 — Launch Arguments Reference

### `sim_pillar_nav_demo.launch.py` (simulation)

| Argument | Default | Description |
|---|---|---|
| `enable_microphone` | `true` | Enable live microphone input |
| `enable_llm` | `true` | Use Ollama — set `false` for rules-only mode |
| `llm_model` | `qwen2.5:7b` | Ollama model name |
| `ollama_host` | `http://localhost:11434` | Ollama server address |
| `knowledge_db_path` | *(auto)* | Path override for the SQLite knowledge database |
| `mute` | `false` | Silence all TTS output |
| `enable_speech_debug` | `true` | Start the speech pipeline aggregator node |
| `enable_knowledge_editor` | `false` | Launch the Tkinter editor alongside the robot |
| `enable_direct_locomotion_interface` | `false` | Direct speech → Nav2 bridge |
| `tour_db_path` | *(auto)* | Path override for the tour waypoint database |

### `bringup.launch.py` (hardware or simulation, no Gazebo)

All arguments above, plus:

| Argument | Default | Description |
|---|---|---|
| `hardware` | `false` | `true` = real robot (disables sim time) |

---

## Troubleshooting

### Ollama is not responding

```bash
curl http://localhost:11434/api/tags
```

If this fails, start the server:

```bash
ollama serve
```

If the model is missing:

```bash
ollama list                  # see what is downloaded
ollama pull qwen2.5:7b       # re-download if needed
```

---

### Robot does not speak

Check TTS is installed:

```bash
which spd-say && spd-say "test"
which espeak  && espeak "test"
```

Install if missing:

```bash
sudo apt install -y speech-dispatcher espeak
```

Check the response topic has traffic:

```bash
ros2 topic echo /speech/response
```

Publish a test message directly to TTS:

```bash
ros2 topic pub --once /speech/response std_msgs/String "data: 'hello'"
```

---

### Nav2 does not accept goals

Check the initial pose was published:

```bash
ros2 topic echo /initialpose --once
```

Publish it manually if needed:

```bash
ros2 topic pub --once /initialpose \
  geometry_msgs/PoseWithCovarianceStamped \
  "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -2.0, y: -0.5, z: 0.0}, orientation: {w: 1.0}}}}"
```

---

### `colcon build` fails with missing packages

```bash
cd /home/karan/in_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
```

---

### `ModuleNotFoundError: No module named 'ollama'`

```bash
pip install ollama
python3 -c "import ollama; print('OK')"
```

---

### Intent is always `no_action`

1. Verify Ollama is reachable: `curl http://localhost:11434/api/tags`
2. Check `speech_command_node` logs — it should print `client=True` on startup.
3. Watch `/speech/debug` to see the raw text and parsed intent side by side.
4. Try the LLM intent test tool interactively:

```bash
ros2 run turtlebot_llm_control llm_intent_test
```

---

### Knowledge editor window does not open

```bash
python3 -c "import tkinter; tkinter._test()"
```

Install Tkinter if missing:

```bash
sudo apt install -y python3-tk
```

---

### Gazebo is very slow or crashes

```bash
export SVGA_VGPU10=0            # disable GPU renderer if on a VM
ros2 launch turtlebot_llm_control sim_pillar_nav_demo.launch.py ...
```

---

## Quick-Start Checklist

Use this before each demo session:

```
[ ] ollama serve          — Ollama server is running in a terminal
[ ] ollama list           — qwen2.5:7b is present
[ ] TURTLEBOT3_MODEL      — exported in the launch terminal
[ ] source install/setup.bash — workspace overlay sourced
[ ] colcon build          — no errors since last code change
[ ] knowledge.db          — at least one entry with X/Y coordinates saved
```

Full one-time setup checklist:

```
[ ] Ubuntu 22.04 LTS installed (x86-64)
[ ] ros-humble-desktop-full installed and sourced
[ ] python3-colcon-common-extensions installed
[ ] TurtleBot 3 packages installed
[ ] Nav2 packages installed
[ ] Gazebo packages installed
[ ] Ollama installed  (ollama --version)
[ ] ollama pull qwen2.5:7b  completed
[ ] pip install ollama  completed
[ ] pip install SpeechRecognition PyAudio opencv-python transforms3d  completed
[ ] sudo apt install speech-dispatcher espeak  completed
[ ] rosdep install --from-paths src --ignore-src -r -y  run
[ ] colcon build  succeeded with no errors
[ ] source /opt/ros/humble/setup.bash  in ~/.bashrc
[ ] source /home/karan/in_ws/install/setup.bash  in ~/.bashrc
[ ] export TURTLEBOT3_MODEL=waffle  in ~/.bashrc
[ ] export GAZEBO_MODEL_PATH=...  in ~/.bashrc
```
