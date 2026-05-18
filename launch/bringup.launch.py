from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    hardware = LaunchConfiguration("hardware")
    enable_microphone = LaunchConfiguration("enable_microphone")
    enable_llm = LaunchConfiguration("enable_llm")
    ollama_model = LaunchConfiguration("ollama_model")
    ollama_url = LaunchConfiguration("ollama_url")
    memory_file = LaunchConfiguration("memory_file")
    tours_dir = LaunchConfiguration("tours_dir")
    whisper_model = LaunchConfiguration("whisper_model")
    mute = LaunchConfiguration("mute")
    enable_speech_debug = LaunchConfiguration("enable_speech_debug")
    use_sim_time = PythonExpression(["'false' if '", hardware, "' == 'true' else 'true'"])

    return LaunchDescription([
        DeclareLaunchArgument("hardware", default_value="false",
                              description="Set true when running on real robot hardware"),
        DeclareLaunchArgument("enable_microphone", default_value="false",
                              description="Use real microphone (true) or /speech/mock_text (false)"),
        DeclareLaunchArgument("enable_llm", default_value="true",
                              description="Enable Ollama LLM brain (false = rule-based only)"),
        DeclareLaunchArgument("ollama_model", default_value="qwen2.5",
                              description="Ollama model name (must be pulled: ollama pull qwen2.5)"),
        DeclareLaunchArgument("ollama_url", default_value="http://localhost:11434/api/chat",
                              description="Ollama API endpoint"),
        DeclareLaunchArgument("memory_file", default_value="~/.ros/robot_memory.json",
                              description="Path to persistent memory JSON file"),
        DeclareLaunchArgument("tours_dir", default_value="~/tours",
                              description="Directory containing tour CSV files"),
        DeclareLaunchArgument("whisper_model", default_value="base",
                              description="Faster-Whisper model size: tiny/base/small/medium/large"),
        DeclareLaunchArgument("mute", default_value="false",
                              description="Suppress TTS audio output"),
        DeclareLaunchArgument("enable_speech_debug", default_value="true",
                              description="Launch speech debug aggregator node"),

        Node(
            package="turtlebot_llm_control",
            executable="speech_to_text_node",
            name="speech_to_text_node",
            output="screen",
            emulate_tty=True,
            parameters=[{
                "use_sim_time": use_sim_time,
                "enable_microphone": enable_microphone,
                "whisper_model": whisper_model,
            }],
        ),

        Node(
            package="turtlebot_llm_control",
            executable="speech_command_node",
            name="speech_command_node",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                "enable_llm": enable_llm,
                "ollama_model": ollama_model,
                "ollama_url": ollama_url,
                "memory_file": memory_file,
            }],
        ),

        Node(
            package="turtlebot_llm_control",
            executable="bt_orchestrator_node",
            name="bt_orchestrator_node",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                "tours_dir": tours_dir,
            }],
        ),

        Node(
            package="turtlebot_llm_control",
            executable="speech_response_node",
            name="speech_response_node",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                "mute": mute,
            }],
        ),

        Node(
            package="turtlebot_llm_control",
            executable="speech_debug_node",
            name="speech_debug_node",
            output="screen",
            condition=IfCondition(enable_speech_debug),
            parameters=[{"use_sim_time": use_sim_time}],
        ),
    ])
