from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    hardware = LaunchConfiguration("hardware")
    enable_microphone = LaunchConfiguration("enable_microphone")
    enable_llm = LaunchConfiguration("enable_llm")
    llm_model = LaunchConfiguration("llm_model")
    ollama_host = LaunchConfiguration("ollama_host")
    knowledge_db_path = LaunchConfiguration("knowledge_db_path")
    mute = LaunchConfiguration("mute")
    enable_speech_debug = LaunchConfiguration("enable_speech_debug")
    enable_direct_locomotion_interface = LaunchConfiguration(
        "enable_direct_locomotion_interface"
    )
    use_sim_time = PythonExpression(["'false' if '", hardware, "' == 'true' else 'true'"])
    return LaunchDescription(
        [
            DeclareLaunchArgument("hardware", default_value="false"),
            DeclareLaunchArgument("enable_microphone", default_value="false"),
            DeclareLaunchArgument("enable_llm", default_value="true"),
            DeclareLaunchArgument("llm_model", default_value="qwen2.5:7b"),
            DeclareLaunchArgument("ollama_host", default_value="http://localhost:11434"),
            DeclareLaunchArgument("knowledge_db_path", default_value=""),
            DeclareLaunchArgument("mute", default_value="false"),
            DeclareLaunchArgument("enable_speech_debug", default_value="true"),
            DeclareLaunchArgument(
                "enable_direct_locomotion_interface",
                default_value="false",
            ),
            Node(
                package="turtlebot_llm_control",
                executable="speech_to_text_node",
                name="speech_to_text_node",
                output="screen",
                parameters=[
                    {
                        "use_sim_time": use_sim_time,
                        "enable_microphone": enable_microphone,
                    }
                ],
            ),
            Node(
                package="turtlebot_llm_control",
                executable="speech_command_node",
                name="speech_command_node",
                output="screen",
                parameters=[
                    {
                        "use_sim_time": use_sim_time,
                        "enable_llm": enable_llm,
                        "llm_model": llm_model,
                        "ollama_host": ollama_host,
                        "knowledge_db_path": knowledge_db_path,
                    }
                ],
            ),
            Node(
                package="turtlebot_llm_control",
                executable="bt_orchestrator_node",
                name="bt_orchestrator_node",
                output="screen",
                parameters=[{"use_sim_time": use_sim_time}],
            ),
            Node(
                package="turtlebot_llm_control",
                executable="follow_me_node",
                name="follow_me_node",
                output="screen",
                parameters=[{"use_sim_time": use_sim_time}],
            ),
            Node(
                package="turtlebot_llm_control",
                executable="speech_response_node",
                name="speech_response_node",
                output="screen",
                parameters=[
                    {
                        "use_sim_time": use_sim_time,
                        "mute": mute,
                    }
                ],
            ),
            Node(
                package="turtlebot_llm_control",
                executable="speech_debug_node",
                name="speech_debug_node",
                output="screen",
                condition=IfCondition(enable_speech_debug),
                parameters=[{"use_sim_time": use_sim_time}],
            ),
            Node(
                package="speech_locomotion_interface",
                executable="listening",
                name="speech_locomotion_interface",
                output="screen",
                condition=IfCondition(enable_direct_locomotion_interface),
            ),
            Node(
                package="turtlebot_llm_control",
                executable="tour_recording_manager",
                name="tour_recording_manager",
                output="screen",
                parameters=[{"use_sim_time": use_sim_time}],
            ),
            Node(
                package="turtlebot_llm_control",
                executable="knowledge_overlay_node",
                name="knowledge_overlay_node",
                output="screen",
                parameters=[
                    {
                        "use_sim_time": use_sim_time,
                        "knowledge_db_path": knowledge_db_path,
                    }
                ],
            ),
        ]
    )
