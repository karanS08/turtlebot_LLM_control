from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    db_path = LaunchConfiguration("db_path")
    return LaunchDescription([
        DeclareLaunchArgument("db_path", default_value=""),
        Node(
            package="tour_manager",
            namespace="",
            executable="tour_manager",
            name="tour_manager",
            parameters=[{"db_path": db_path}],
        ),
        Node(
            package="tour_manager",
            namespace="",
            executable="tour_saver",
            name="tour_saver",
        ),
        Node(
            package="tour_manager",
            namespace="",
            executable="waypoint_visualizer",
            name="waypoint_visualizer",
            parameters=[{"db_path": db_path}],
        ),
        Node(
            package="robot_tour",
            namespace="",
            executable="tour_guide_start",
        ),
        Node(
            package="speech_locomotion_interface",
            namespace="",
            executable="listening",
        )
    ])
