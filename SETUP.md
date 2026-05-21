# Environment Setup Guide

This guide takes you from a clean Ubuntu 22.04 machine to a fully running TurtleBot3 Social Guide Robot system — both the robot workspace and the LLM workspace.

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Operating system | Ubuntu 22.04 LTS |
| ROS2 | Humble Hawksbill |
| Python | 3.10 (ships with Ubuntu 22.04) |
| GPU | Optional — CPU is sufficient for `faster-whisper base` model |

---

## 1. Install ROS2 Humble

Follow the official guide or use these commands:

```bash
# Set locale
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS2 apt repository
sudo apt install -y software-properties-common curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list

# Install
sudo apt update
sudo apt install -y ros-humble-desktop

# Source in every terminal (or add to ~/.bashrc)
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 2. Install ROS2 Build Tools

```bash
sudo apt install -y python3-colcon-common-extensions python3-rosdep python3-pip

# Initialise rosdep (skip if already done)
sudo rosdep init
rosdep update
```

---

## 3. Install TurtleBot3 Packages

```bash
sudo apt install -y \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-msgs \
  ros-humble-turtlebot3-simulations \
  ros-humble-nav2-bringup \
  ros-humble-navigation2 \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros2-control

# Set your TurtleBot3 model (waffle_pi is the default in this project)
echo "export TURTLEBOT3_MODEL=waffle_pi" >> ~/.bashrc
source ~/.bashrc
```

---

## 4. Install Python Dependencies

### Core robot workspace dependencies

```bash
pip3 install \
  pyqt5 \
  numpy \
  scipy \
  pyyaml \
  pillow
```

### LLM workspace dependencies

```bash
pip3 install \
  openai \
  speechrecognition \
  pyaudio \
  pydub
```

> **`pyaudio` note:** If `pip install pyaudio` fails, install the system library first:
> ```bash
> sudo apt install -y portaudio19-dev
> pip3 install pyaudio
> ```

### Speech-to-text: faster-whisper (offline, no API key needed)

```bash
pip3 install faster-whisper
```

The first launch downloads the `base` Whisper model (~145 MB) to `~/.cache/huggingface/hub/`. This requires an internet connection once. After that it runs fully offline.

Verify the install:
```bash
python3 -c "
from faster_whisper import WhisperModel
m = WhisperModel('base', device='cpu', compute_type='int8')
print('faster-whisper OK — model loaded')
"
```

### Text-to-speech (waypoint announcer)

```bash
sudo apt install -y speech-dispatcher
# Quick test
spd-say "Hello from the robot"
```

---

## 5. Install and Set Up Ollama

Ollama runs large language models locally at zero API cost. It is used to parse ambiguous speech commands.

### Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Ollama installs as a system service and starts automatically. Verify:

```bash
ollama --version
```

### Pull the default model

This project defaults to `qwen2.5-coder:latest` (~4 GB):

```bash
ollama pull qwen2.5-coder:latest
```

Lighter alternatives (faster on CPU, less accurate):

```bash
ollama pull qwen2.5:3b       # ~2 GB, fastest
ollama pull llama3.2:3b      # ~2 GB, good general purpose
```

### Start Ollama (if not running as a service)

```bash
ollama serve &
# Test it
curl http://localhost:11434/v1/models
```

### Change the model used by the launch file

Pass `llm_model` as a launch argument:
```bash
ros2 launch turtlebot_llm_control bringup.launch.py llm_model:=llama3.2:3b
```

---

## 6. Alternative LLM Providers (optional)

If you prefer a cloud API instead of Ollama, the engine supports **Groq** and **OpenAI**.

### Groq (free tier, very fast)

```bash
pip3 install groq
```

Create `~/.groq.key` and paste your key from [console.groq.com](https://console.groq.com):
```bash
echo "YOUR_GROQ_API_KEY" > ~/.groq.key
```

Launch with:
```bash
ros2 launch turtlebot_llm_control bringup.launch.py \
  llm_provider:=groq \
  llm_model:=llama-3.1-70b-versatile \
  llm_api_key_path:=$HOME/.groq.key
```

### OpenAI

```bash
pip3 install openai
echo "YOUR_OPENAI_API_KEY" > ~/.openai.key
```

Launch with:
```bash
ros2 launch turtlebot_llm_control bringup.launch.py \
  llm_provider:=openai \
  llm_model:=gpt-4o-mini \
  llm_api_key_path:=$HOME/.openai.key
```

Alternatively, set the environment variable:
```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"
```

---

## 7. Build the Robot Workspace

```bash
cd ~/Development/robot_gpt/turtlebot_social_guide   # adjust path to yours

source /opt/ros/humble/setup.bash

# Install ROS package dependencies
rosdep install --from-paths src --ignore-src -r -y

# Build
colcon build

# Source
source install/setup.bash
```

Add to `~/.bashrc`:
```bash
echo "source ~/Development/robot_gpt/turtlebot_social_guide/install/setup.bash" >> ~/.bashrc
```

---

## 8. Build the LLM Workspace

```bash
cd ~/Development/robot_gpt/llm_ws_1

source /opt/ros/humble/setup.bash

# Build
colcon build

# Source
source install/setup.bash
```

Add to `~/.bashrc`:
```bash
echo "source ~/Development/robot_gpt/llm_ws_1/install/setup.bash" >> ~/.bashrc
```

---

## 9. Required Environment Variables

Add these to your `~/.bashrc`:

```bash
# ROS2
source /opt/ros/humble/setup.bash

# Robot workspace
source ~/Development/robot_gpt/turtlebot_social_guide/install/setup.bash

# LLM workspace
source ~/Development/robot_gpt/llm_ws_1/install/setup.bash

# TurtleBot3 model — MUST match the model in the Nav2 params YAML
export TURTLEBOT3_MODEL=waffle_pi

# Gazebo model path for TurtleBot3
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models
```

Apply:
```bash
source ~/.bashrc
```

---

## 10. First-Run Checklist

Run these in order in separate terminals. Each terminal needs the environment sourced.

### Terminal 1 — Robot workspace (Gazebo + Nav2 + tour nodes)

```bash
export TURTLEBOT3_MODEL=waffle_pi
source ~/.bashrc
ros2 launch tour_manager locomotion_test.launch.py
```

Wait until you see:
- Gazebo window opens with TurtleBot3
- RViz opens with the map
- `tour_manager`, `tsp_gui_node` appear in `ros2 node list`

### Terminal 2 — LLM workspace (speech + intent + waypoint speaker)

```bash
source ~/.bashrc
ros2 launch turtlebot_llm_control bringup.launch.py \
  enable_microphone:=true \
  enable_llm:=true \
  llm_provider:=ollama \
  llm_model:=qwen2.5-coder:latest
```

### Terminal 3 — Monitoring (optional but useful)

```bash
source ~/.bashrc
# Watch what the robot hears
ros2 topic echo /speech/intent

# Watch emotion states
ros2 topic echo /robot/emotion

# Watch waypoint arrival events
ros2 topic echo /talk_command
```

---

## 11. Saving Waypoints and Descriptions

### Save a waypoint (using the TF pose)

Navigate to a location in the map, then:
```bash
ros2 topic pub --once /save_tour_command std_msgs/msg/String "{data: save}"
```

### Add descriptions to waypoints

Descriptions are stored in the `description` column of `tours.db`. You can add them with any SQLite client:

```bash
# Open the database (from the robot workspace root)
sqlite3 ~/Development/robot_gpt/turtlebot_social_guide/tours.db

# Add a description to the first saved waypoint (row 1)
UPDATE tours SET description = 'Welcome to the entrance hall. This is where visitors check in.'
WHERE rowid = 1;

# Add a description to the second waypoint
UPDATE tours SET description = 'This is the research laboratory. The team works on robotics and AI here.'
WHERE rowid = 2;

.quit
```

When the robot reaches that waypoint, `waypoint_speaker_node` will look up and speak the description automatically.

---

## 12. Troubleshooting

### Gazebo or Nav2 does not open

Make sure `TURTLEBOT3_MODEL` is set **in the same terminal** before running the launch:
```bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch tour_manager locomotion_test.launch.py
```

### `faster-whisper` model download hangs or fails

```bash
export HF_HOME=~/.cache/huggingface
python3 -c "from faster_whisper import WhisperModel; WhisperModel('base')"
```

### Ollama model not found

```bash
ollama list          # see what is downloaded
ollama pull qwen2.5-coder:latest
```

### Speech is not recognised / speech_to_text_node crashes

Check your microphone is detected:
```bash
python3 -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

### `spd-say` not found (no TTS)

```bash
sudo apt install -y speech-dispatcher
spd-say "test"
```

### TSP GUI does not appear

Confirm the `tsp_gui_node` is running:
```bash
ros2 node list | grep tsp_gui
```

Then trigger it:
```bash
ros2 topic pub --once /tsp_gui/show std_msgs/msg/String "{data: show}"
```

### Waypoint speaker not announcing

Check the node is running:
```bash
ros2 node list | grep waypoint_speaker
```

Check it can reach tours.db:
```bash
ros2 topic pub --once /talk_command std_msgs/msg/String "{data: 'Arrived at waypoint 0'}"
ros2 topic echo /done_speaking
```

---

## 13. Package Summary

| Package / Module | Location | Build system |
|-----------------|----------|-------------|
| `tour_manager` | `turtlebot_social_guide/src/tour_manager` | `colcon` (ament_python) |
| `robot_tour` | `turtlebot_social_guide/src/robot_tour` | `colcon` (ament_cmake) |
| `speech_locomotion_interface` | `turtlebot_social_guide/src/speech_locomotion_interface` | `colcon` (ament_python) |
| `docking` | `turtlebot_social_guide/src/docking` | `colcon` (ament_python) |
| `social_robot_interfaces` | `turtlebot_social_guide/src/social_robot_interfaces` | `colcon` (ament_cmake) |
| `turtlebot_llm_control` | `llm_ws_1/src/turtlebot_LLM_control` | `colcon` (ament_python) |
