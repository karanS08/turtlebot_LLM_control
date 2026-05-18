from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="turtlebot_llm_control",
            executable="waypoint_recorder",
            name="waypoint_recorder",
            output="screen",
            emulate_tty=True,
        ),
    ])
