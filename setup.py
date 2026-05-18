from glob import glob
from setuptools import find_packages, setup


package_name = "turtlebot_llm_control"


setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="karan",
    maintainer_email="karan@example.com",
    description="LLM-driven speech, routing, and behaviour-tree orchestration for the Social Tour Guide Robot.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "speech_command_node = turtlebot_llm_control.speech_command_node:main",
            "speech_to_text_node = turtlebot_llm_control.speech_to_text_node:main",
            "bt_orchestrator_node = turtlebot_llm_control.bt_orchestrator_node:main",
            "speech_response_node = turtlebot_llm_control.speech_response_node:main",
            "speech_debug_node = turtlebot_llm_control.speech_debug_node:main",
            "waypoint_recorder = turtlebot_llm_control.waypoint_recorder:main",
            "tour_planner = turtlebot_llm_control.tour_planner:main",
        ],
    },
)
