# turtlebot_llm_control

This package is a practical starting point for a TurtleBot assistant that combines:

- speech-to-text command intake
- lightweight intent extraction suitable for replacement by an LLM
- navigation goal triggering through ROS2/Nav2
- behavior-tree-style task orchestration
- spoken responses and task-state tracking

## Package layout

- `speech_command_node`: converts speech text into structured command tokens.
- `bt_orchestrator_node`: manages robot mode transitions and action execution.
- `follow_me_node`: follows a chosen colored target with a simple image-based chase controller.
- `speech_response_node`: plays spoken replies from `/speech/response`.
- `speech_debug_node`: republishes speech-only debug events on `/speech/debug`.

## Topics

- `/speech/text` (`std_msgs/String`): raw recognized speech text.
- `/speech/intent` (`std_msgs/String`): JSON command token emitted by the speech node.
- `/speech/response` (`std_msgs/String`): robot verbal response text.
- `/speech/debug` (`std_msgs/String`): isolated speech pipeline debug stream.
- `/tour/status` (`std_msgs/String`): JSON summary of current task state.
- `/follow_me/control` (`std_msgs/String`): `start`, `start:<color>`, `color:<color>`, or `stop`.
- `/follow_me/status` (`std_msgs/String`): tracker and follow-controller state.
- `/follow_me/debug/compressed` (`sensor_msgs/CompressedImage`): follow-mode debug image.
- `/exploration/control` (`std_msgs/String`): `start` or `stop` autonomous exploration.
- `/exploration/status` (`std_msgs/String`): explorer state and recovery messages.
- `/manual_override/control` (`std_msgs/String`): `on` or `off` to hand control to teleop and then return to autonomy.

## Notes

- The speech node currently uses rule-based parsing so you can test quickly.
- The parser is intentionally isolated so you can later swap in Whisper, Vosk, or an LLM.
- The route manager stores routes in memory for now; persistent storage can be added next.
- The orchestrator now starts and stops the dedicated follow controller for commands such as `follow me` or `follow the yellow bin`.
- The reactive navigation node uses `/scan` and publishes `/cmd_vel`, and now prefers wall-parallel motion, slow front approach, then committed turn or dead-end escape.
- The bin detector assumes the bins are visually red, green, blue, or yellow and distinct from the floor/walls; tune HSV bounds if your Gazebo lighting/materials differ.
- `autonomous_bin_mission.launch.py` is the recommended main demo launch for exploration, Cartographer mapping, bin finding, memory, and speech control.
- `remembered_bin_navigation.launch.py` is the post-mapping launch for voice commands such as `go to the red bin`.
- Manual override pauses exploration and reactive autonomy so `turtlebot3_teleop` can safely own `/cmd_vel`.
- The more detailed run instructions are in `GUIDE.md`.
