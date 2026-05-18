"""
sim_bringup.launch.py
=====================
One-command simulation bringup for ARIA Social Tour Guide Robot.

Starts in order (with delays so each layer is ready before the next):
  T+0s   Gazebo  (TurtleBot3 world)
  T+4s   Tour Manager  (waypoint DB + tour services)
  T+8s   Nav2  (AMCL localisation + path planner)
  T+18s  LLM Control Stack  (STT, LLM brain, BT, TTS, debug)

Usage:
  ros2 launch turtlebot_llm_control sim_bringup.launch.py map:=~/maps/my_map.yaml

Arguments:
  map                 Full path to .yaml map file  (default: ~/maps/my_map.yaml)
  turtlebot3_model    burger / waffle / waffle_pi  (default: burger)
  ollama_model        Ollama model name             (default: qwen2.5)
  whisper_model       tiny / base / small / medium  (default: base)
  tours_dir           Directory with tour CSVs      (default: ~/tours)
  enable_llm          true / false                  (default: true)
  enable_speech_debug true / false                  (default: true)
"""

import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# ---------------------------------------------------------------------------
# Resolve all package share paths at load time (before any action executes).
# This avoids FindPackageShare substitution failing inside TimerActions, and
# ensures TURTLEBOT3_MODEL is set before navigation2.launch.py is imported
# (which reads os.environ['TURTLEBOT3_MODEL'] at module level).
# ---------------------------------------------------------------------------

_TB3_MODEL = os.environ.get("TURTLEBOT3_MODEL", "burger")
os.environ["TURTLEBOT3_MODEL"] = _TB3_MODEL   # must be set before nav2 import

_GAZEBO_LAUNCH = os.path.join(
    get_package_share_directory("turtlebot3_gazebo"),
    "launch", "turtlebot3_world.launch.py",
)
_NAV2_LAUNCH = os.path.join(
    get_package_share_directory("turtlebot3_navigation2"),
    "launch", "navigation2.launch.py",
)
# Resolve the nav2 params path as a plain string at load time to avoid the
# circular LaunchConfiguration reference in navigation2.launch.py that causes
# params_file to resolve to '' and crash bringup_launch.py's RewrittenYaml.
_ROS_DISTRO = os.environ.get("ROS_DISTRO", "")
_NAV2_PARAMS = os.path.join(
    get_package_share_directory("turtlebot3_navigation2"),
    "param", _ROS_DISTRO, f"{_TB3_MODEL}.yaml",
) if _ROS_DISTRO else os.path.join(
    get_package_share_directory("turtlebot3_navigation2"),
    "param", f"{_TB3_MODEL}.yaml",
)

try:
    _TOUR_MGR_PARAMS = os.path.join(
        get_package_share_directory("tour_manager"),
        "config", "tour_manager_params.yaml",
    )
    _TOUR_MGR_OK = True
except Exception:
    _TOUR_MGR_PARAMS = ""
    _TOUR_MGR_OK = False


def generate_launch_description():

    # ------------------------------------------------------------------ args
    map_arg = DeclareLaunchArgument(
        "map",
        default_value=str(Path("~/maps/my_map.yaml").expanduser()),
        description="Full path to Nav2 map YAML file",
    )
    model_arg = DeclareLaunchArgument(
        "turtlebot3_model", default_value=_TB3_MODEL,
        description="TurtleBot3 model: burger / waffle / waffle_pi",
    )
    ollama_model_arg = DeclareLaunchArgument(
        "ollama_model", default_value="qwen2.5",
        description="Ollama model (must be pulled first: ollama pull qwen2.5)",
    )
    whisper_model_arg = DeclareLaunchArgument(
        "whisper_model", default_value="base",
        description="Faster-Whisper model size: tiny / base / small / medium",
    )
    tours_dir_arg = DeclareLaunchArgument(
        "tours_dir", default_value=str(Path("~/tours").expanduser()),
        description="Directory containing tour CSV files",
    )
    enable_llm_arg = DeclareLaunchArgument(
        "enable_llm", default_value="true",
        description="Enable Ollama LLM (false = rule-based fallback only)",
    )
    enable_debug_arg = DeclareLaunchArgument(
        "enable_speech_debug", default_value="true",
        description="Launch colour-coded speech debug monitor",
    )

    map_path      = LaunchConfiguration("map")
    ollama_model  = LaunchConfiguration("ollama_model")
    whisper_model = LaunchConfiguration("whisper_model")
    tours_dir     = LaunchConfiguration("tours_dir")
    enable_llm    = LaunchConfiguration("enable_llm")
    enable_debug  = LaunchConfiguration("enable_speech_debug")

    # ------------------------------------------------------------------ T+0s  Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(_GAZEBO_LAUNCH),
    )

    # ------------------------------------------------------------------ T+4s  Tour Manager
    # Nodes are inlined (not via IncludeLaunchDescription) so the params path
    # is already resolved as a plain string — avoids FindPackageShare lazy
    # substitution returning '' when evaluated inside TimerAction.
    if _TOUR_MGR_OK:
        _p = [_TOUR_MGR_PARAMS]
        _tour_mgr_nodes = [
            Node(package="tour_manager",              executable="tour_manager",    name="tour_manager",  parameters=_p),
            Node(package="tour_manager",              executable="tour_saver",      name="tour_saver",    parameters=_p),
            Node(package="robot_tour",                executable="tour_guide_start",                      parameters=_p),
            Node(package="robot_tour",                executable="subtour_start",   name="subtour",       parameters=_p),
            Node(package="docking",                   executable="dock_listener",                         parameters=_p),
            Node(package="speech_locomotion_interface", executable="listening",                            parameters=_p),
        ]
        tour_manager = TimerAction(period=4.0, actions=_tour_mgr_nodes)
    else:
        import warnings
        warnings.warn("tour_manager package not found — skipping tour_manager launch")
        tour_manager = None

    # ------------------------------------------------------------------ T+8s  Nav2
    nav2 = TimerAction(
        period=8.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(_NAV2_LAUNCH),
                launch_arguments={
                    "use_sim_time": "true",
                    "map": map_path,
                    "params_file": _NAV2_PARAMS,
                }.items(),
            )
        ],
    )

    # ------------------------------------------------------------------ T+18s  LLM Control Stack
    llm_nodes = TimerAction(
        period=18.0,
        actions=[
            Node(
                package="turtlebot_llm_control",
                executable="speech_to_text_node",
                name="speech_to_text_node",
                output="screen",
                emulate_tty=True,
                parameters=[{
                    "use_sim_time": True,
                    "enable_microphone": False,
                    "require_wake_word": True,
                    "whisper_model": whisper_model,
                }],
            ),
            Node(
                package="turtlebot_llm_control",
                executable="speech_command_node",
                name="speech_command_node",
                output="screen",
                parameters=[{
                    "use_sim_time": True,
                    "enable_llm": enable_llm,
                    "ollama_model": ollama_model,
                    "ollama_url": "http://localhost:11434/api/chat",
                    "memory_file": str(Path("~/.ros/robot_memory.json").expanduser()),
                }],
            ),
            Node(
                package="turtlebot_llm_control",
                executable="bt_orchestrator_node",
                name="bt_orchestrator_node",
                output="screen",
                parameters=[{
                    "use_sim_time": True,
                    "tours_dir": tours_dir,
                }],
            ),
            Node(
                package="turtlebot_llm_control",
                executable="speech_response_node",
                name="speech_response_node",
                output="screen",
                parameters=[{"use_sim_time": True, "mute": False}],
            ),
            Node(
                package="turtlebot_llm_control",
                executable="speech_debug_node",
                name="speech_debug_node",
                output="screen",
                emulate_tty=True,
                parameters=[{"use_sim_time": True}],
            ),
        ],
    )

    # ------------------------------------------------------------------ assemble
    ld_actions = [
        map_arg, model_arg, ollama_model_arg, whisper_model_arg,
        tours_dir_arg, enable_llm_arg, enable_debug_arg,
        gazebo,
        nav2,
        llm_nodes,
    ]
    if tour_manager is not None:
        ld_actions.insert(ld_actions.index(nav2), tour_manager)

    return LaunchDescription(ld_actions)
