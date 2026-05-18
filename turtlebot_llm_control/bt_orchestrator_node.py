import csv
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import FollowWaypoints, NavigateToPose
from std_msgs.msg import String

import rclpy
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node

from turtlebot_llm_control.behavior_tree import (
    ActionNode,
    ConditionNode,
    FallbackNode,
    NodeStatus,
    SequenceNode,
)
from turtlebot_llm_control.models import (
    ControllerStatus,
    DialogueMemory,
    IntentToken,
    RobotExpression,
    TaskState,
)

try:
    from social_robot_interfaces.srv import Tours as ToursSrv
    _TOURS_SRV_AVAILABLE = True
except ImportError:
    _TOURS_SRV_AVAILABLE = False


class BehaviorTreeOrchestrator(Node):
    def __init__(self):
        super().__init__("bt_orchestrator_node")

        self.status = ControllerStatus()
        self.memory = DialogueMemory()
        self.pending_intent: Optional[IntentToken] = None
        self.pending_goal_location: str = ""
        self.pending_goal_pose: Optional[tuple] = None
        self.nav_goal_handle: Optional[ClientGoalHandle] = None
        self.nav_result_future = None
        self.nav_in_progress = False
        self.nav_request_token = 0
        self.localization_ok = True

        # Tour state
        self._current_tour_name: str = ""
        self._tour_descriptions: List[str] = []
        self._tour_waypoint_index: int = 0
        self._follow_wp_goal_handle = None

        # Navigate failure tracking (resets on success)
        self._nav_fail_count: int = 0

        # Waypoint cache (avoids a service round-trip on every navigate intent)
        self._wp_cache: List = []
        self._wp_cache_time: float = 0.0
        self._WP_CACHE_TTL: float = 30.0

        # Parameters
        self.tours_dir = str(
            Path(
                str(self.declare_parameter("tours_dir", "~/tours").value)
            ).expanduser()
        )

        # Subscriptions
        self.create_subscription(String, "/speech/intent", self._on_intent, 10)

        # Publishers
        self.response_pub = self.create_publisher(String, "/speech/response", 10)
        self.status_pub = self.create_publisher(String, "/tour/status", 10)
        self.expression_pub = self.create_publisher(String, "/robot/expression", 10)
        self.manual_override_pub = self.create_publisher(String, "/manual_override/control", 10)
        self.follow_control_pub = self.create_publisher(String, "/follow_me/control", 10)

        # Action clients
        self.nav_client = ActionClient(self, NavigateToPose, "/navigate_to_pose")
        self.follow_wp_client = ActionClient(self, FollowWaypoints, "/follow_waypoints")

        # Service client for tour_retrieve (social_guide)
        self.tour_retrieve_client = None
        if _TOURS_SRV_AVAILABLE:
            self.tour_retrieve_client = self.create_client(ToursSrv, "tour_retrieve")
        else:
            self.get_logger().warning(
                "social_robot_interfaces not found — tour_retrieve service unavailable"
            )

        # Behaviour tree + timer
        self.behavior_tree = self._build_tree()
        self.create_timer(1.0, self._tick)

        self._set_expression(RobotExpression.IDLE)
        self.get_logger().info("Behaviour-tree orchestrator ready.")

    # ------------------------------------------------------------------
    # Expression helper
    # ------------------------------------------------------------------

    def _set_expression(self, state: str):
        self.expression_pub.publish(String(data=state))

    # ------------------------------------------------------------------
    # Behaviour tree
    # ------------------------------------------------------------------

    def _build_tree(self):
        return FallbackNode([
            SequenceNode([
                ConditionNode(lambda: not self.localization_ok),
                ActionNode(self._recover_localization),
            ]),
            SequenceNode([
                ConditionNode(self._has_interruption),
                ActionNode(self._pause_task),
                ActionNode(self._respond_to_user),
                ActionNode(self._resume_task),
            ]),
            SequenceNode([
                ConditionNode(lambda: self.status.task_state == TaskState.TOURING),
                ActionNode(self._explain_current_stop),
                ActionNode(self._sync_gesture_stub),
            ]),
            SequenceNode([
                ConditionNode(lambda: self.status.task_state == TaskState.FOLLOWING),
                ActionNode(self._follow_user_stub),
            ]),
            SequenceNode([
                ConditionNode(lambda: self.status.task_state == TaskState.NAVIGATING),
                ActionNode(self._navigate_to_pending_goal),
            ]),
        ])

    def _tick(self):
        self.behavior_tree.tick()
        self._publish_status()

    # ------------------------------------------------------------------
    # Intent handling
    # ------------------------------------------------------------------

    def _on_intent(self, msg: String):
        token = IntentToken.from_json(msg.data)
        self.pending_intent = token
        self._apply_intent(token)
        self._publish_status()

    def _apply_intent(self, token: IntentToken):
        intent = token.intent

        if intent == "is_alive":
            self._say(token.response)
            return

        if intent == "no_action":
            self.status.task_state = TaskState.IDLE
            self._set_expression(RobotExpression.IDLE)
            self._say(token.response)
            return

        if intent == "follow":
            self.status.task_state = TaskState.FOLLOWING
            self._set_expression(RobotExpression.NAVIGATING)
            self.follow_control_pub.publish(String(data="start:yellow"))
            self._say(token.response)
            return

        if intent == "stop":
            self.memory.paused_task = self.status.task_state
            self.status.task_state = TaskState.IDLE
            self.status.is_paused = False
            self._cancel_nav_goal()
            self._cancel_follow_waypoints()
            self.follow_control_pub.publish(String(data="stop"))
            self._set_expression(RobotExpression.IDLE)
            self._say(token.response)
            return

        if intent == "stop_navigation":
            self._cancel_nav_goal()
            self._cancel_follow_waypoints()
            self.status.task_state = TaskState.IDLE
            self._set_expression(RobotExpression.IDLE)
            self._say(token.response)
            return

        if intent == "pause":
            self.memory.paused_task = self.status.task_state
            self.status.task_state = TaskState.PAUSED
            self.status.is_paused = True
            self.follow_control_pub.publish(String(data="stop"))
            self._set_expression(RobotExpression.IDLE)
            self._say(token.response)
            return

        if intent == "resume":
            paused = self.memory.paused_task or TaskState.IDLE
            self.status.task_state = paused
            self.status.is_paused = False
            if paused == TaskState.FOLLOWING:
                self.follow_control_pub.publish(String(data="start:yellow"))
                self._set_expression(RobotExpression.NAVIGATING)
            self._say(token.response)
            return

        if intent == "navigate":
            label = (token.label or token.location or "").strip()
            pose = self._resolve_waypoint(label)
            if pose is not None:
                self._nav_fail_count = 0
                self.pending_goal_pose = (
                    pose.pose.position.x, pose.pose.position.y, label
                )
                self.pending_goal_location = label
                self.status.current_location = token.location
                self.status.task_state = TaskState.NAVIGATING
                self._set_expression(RobotExpression.NAVIGATING)
                self._say(token.response)
            else:
                self._nav_fail_count += 1
                self._say_location_not_found(label)
            return

        if intent in ("start_tour", "replay_route"):
            self._handle_start_tour(token)
            return

        if intent == "save_waypoint":
            self._say(token.response or "Saving current position as a waypoint.")
            return

        if intent == "dock":
            self._say(token.response or "Returning to home base.")
            return

        if intent == "manual_override_on":
            self.status.task_state = TaskState.PAUSED
            self.follow_control_pub.publish(String(data="stop"))
            self.manual_override_pub.publish(String(data="on"))
            self._say(token.response)
            return

        if intent == "manual_override_off":
            self.status.task_state = TaskState.IDLE
            self.manual_override_pub.publish(String(data="off"))
            self._say(token.response)
            return

        if intent == "explain":
            self.memory.last_question = token.utterance
            location = token.location or self.status.current_location or "this area"
            self.memory.last_response = token.response or f"{location} is one of the tour stops."
            self._set_expression(RobotExpression.EXPLAINING)
            self._say(self.memory.last_response)
            return

        # Fallback — say whatever the LLM produced
        self._say(token.response)

    # ------------------------------------------------------------------
    # Tour CSV loading + execution
    # ------------------------------------------------------------------

    def _load_tour_csv(self, tour_name: str) -> tuple:
        """Return (list[int], list[str]) of waypoint indices and descriptions."""
        candidates = [
            os.path.join(self.tours_dir, f"{tour_name}.csv"),
            os.path.join(self.tours_dir, f"tour{tour_name}.csv"),
        ]
        for path in candidates:
            if os.path.exists(path):
                indices, descs = [], []
                with open(path, newline="") as f:
                    for row in csv.reader(f):
                        if not row or str(row[0]).startswith("#"):
                            continue
                        try:
                            indices.append(int(row[0].strip()))
                            descs.append(row[1].strip() if len(row) > 1 else "")
                        except (ValueError, IndexError):
                            continue
                self.get_logger().info(
                    f"Loaded tour '{tour_name}' from {path}: {len(indices)} stops"
                )
                return indices, descs
        self.get_logger().warning(
            f"Tour CSV not found for '{tour_name}' in {self.tours_dir}"
        )
        return [], []

    def _get_all_waypoints(self) -> list:
        """Fetch all PoseStamped waypoints from social_guide's tour_retrieve service."""
        if self.tour_retrieve_client is None:
            return []
        if not self.tour_retrieve_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warning("tour_retrieve service not available")
            return []
        req = ToursSrv.Request()
        req.idx = 0
        future = self.tour_retrieve_client.call_async(req)
        deadline = time.time() + 4.0
        while not future.done() and time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
        if future.done():
            return list(future.result().tour)
        self.get_logger().warning("tour_retrieve timed out")
        return []

    def _handle_start_tour(self, token: IntentToken):
        tour_name = token.label or "1"
        self._current_tour_name = tour_name
        indices, descriptions = self._load_tour_csv(tour_name)

        if not indices:
            self._say(
                f"I couldn't find tour '{tour_name}'. "
                "Please use the tour planner to create it first."
            )
            return

        all_wps = self._get_all_waypoints()
        if not all_wps:
            self._say("I can't reach the waypoint database right now.")
            return

        selected_poses, selected_descs = [], []
        for idx, desc in zip(indices, descriptions):
            if 0 <= idx < len(all_wps):
                selected_poses.append(all_wps[idx])
                selected_descs.append(desc)
            else:
                self.get_logger().warning(f"Waypoint index {idx} out of range, skipping")

        if not selected_poses:
            self._say("No valid waypoints found for this tour.")
            return

        self.status.task_state = TaskState.TOURING
        self.status.current_route = tour_name
        self.memory.active_route = tour_name
        self.memory.current_stop_index = 0
        self._set_expression(RobotExpression.NAVIGATING)
        self._say(
            token.response
            or f"Starting tour '{tour_name}' with {len(selected_poses)} stops. Let's go!"
        )
        self._send_follow_waypoints(selected_poses, selected_descs)

    def _send_follow_waypoints(self, poses: list, descriptions: list):
        self._tour_descriptions = descriptions
        self._tour_waypoint_index = -1

        if not self.follow_wp_client.wait_for_server(timeout_sec=3.0):
            self.get_logger().warning("/follow_waypoints action not available")
            return

        goal = FollowWaypoints.Goal()
        goal.poses = poses
        future = self.follow_wp_client.send_goal_async(
            goal, feedback_callback=self._fw_feedback
        )
        future.add_done_callback(self._fw_goal_response)

    def _fw_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().warning("follow_waypoints goal rejected")
            self.status.task_state = TaskState.IDLE
            return
        self._follow_wp_goal_handle = handle
        handle.get_result_async().add_done_callback(self._fw_result)

    def _fw_feedback(self, feedback_msg):
        idx = feedback_msg.feedback.current_waypoint
        if idx == self._tour_waypoint_index:
            return
        self._tour_waypoint_index = idx
        self.memory.current_stop_index = idx
        desc = (
            self._tour_descriptions[idx]
            if idx < len(self._tour_descriptions)
            else ""
        )
        if desc:
            self._set_expression(RobotExpression.EXPLAINING)
            self._say(desc)

    def _fw_result(self, future):
        result = future.result()
        missed = getattr(result.result, "missed_waypoints", [])
        self.get_logger().info(f"Tour complete. Missed: {missed}")
        self.status.task_state = TaskState.IDLE
        self._current_tour_name = ""
        self._set_expression(RobotExpression.IDLE)
        self._say("We have completed the tour. Thank you for joining me!")

    def _cancel_follow_waypoints(self):
        if self._follow_wp_goal_handle is not None:
            self._follow_wp_goal_handle.cancel_goal_async()
            self._follow_wp_goal_handle = None

    # ------------------------------------------------------------------
    # BT action stubs
    # ------------------------------------------------------------------

    def _has_interruption(self) -> bool:
        return self.status.task_state == TaskState.PAUSED

    def _pause_task(self) -> NodeStatus:
        return NodeStatus.SUCCESS

    def _respond_to_user(self) -> NodeStatus:
        return NodeStatus.SUCCESS

    def _resume_task(self) -> NodeStatus:
        return NodeStatus.SUCCESS

    def _explain_current_stop(self) -> NodeStatus:
        return NodeStatus.SUCCESS

    def _sync_gesture_stub(self) -> NodeStatus:
        self.get_logger().debug("Gesture sync placeholder — wire Pepper gestures here.")
        return NodeStatus.SUCCESS

    def _follow_user_stub(self) -> NodeStatus:
        self.get_logger().debug("Follow mode active.")
        return NodeStatus.RUNNING

    def _recover_localization(self) -> NodeStatus:
        self.status.task_state = TaskState.RECOVERING
        self._say("Localization confidence is low. Attempting recovery.")
        self.localization_ok = True
        self.status.task_state = TaskState.IDLE
        return NodeStatus.SUCCESS

    # ------------------------------------------------------------------
    # Waypoint resolution helpers
    # ------------------------------------------------------------------

    def _get_cached_waypoints(self) -> list:
        """Return waypoints from cache, refreshing if stale."""
        now = time.time()
        if self._wp_cache and (now - self._wp_cache_time) < self._WP_CACHE_TTL:
            return self._wp_cache
        wps = self._get_all_waypoints()
        if wps:
            self._wp_cache = wps
            self._wp_cache_time = now
        return self._wp_cache

    def _resolve_waypoint(self, label: str):
        """Try to resolve a label (numeric index or name) to a PoseStamped.

        Returns PoseStamped on success, None if not found.
        """
        if not label:
            return None
        all_wps = self._get_cached_waypoints()
        if not all_wps:
            return None

        # Numeric index: "3", "waypoint 3", "stop 3"
        for token_part in label.replace("waypoint", "").replace("stop", "").split():
            try:
                idx = int(token_part.strip())
                if 0 <= idx < len(all_wps):
                    return all_wps[idx]
            except ValueError:
                continue

        # Fuzzy word-to-number ("one"→1, "two"→2, …)
        _WORDS = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        }
        for word, num in _WORDS.items():
            if word in label.lower() and 0 <= num < len(all_wps):
                return all_wps[num]

        return None

    def _list_available_tours(self) -> List[str]:
        """Return tour names (CSV basenames without extension) from tours_dir."""
        try:
            return sorted(
                p.stem for p in Path(self.tours_dir).glob("*.csv")
            )
        except Exception:
            return []

    def _say_location_not_found(self, label: str):
        """Tell the user the location wasn't found, listing what IS available."""
        all_wps = self._get_cached_waypoints()
        n = len(all_wps)
        tours = self._list_available_tours()

        if n == 0:
            self._say(
                f"I couldn't find '{label}' and the waypoint database isn't available right now. "
                "Please make sure the social guide nodes are running."
            )
            self.status.task_state = TaskState.IDLE
            return

        # Base "not found" message
        base = f"I couldn't find a place called '{label}'." if label else "I'm not sure where to go."

        if self._nav_fail_count >= 3:
            # After 3+ failed attempts give concrete examples
            example_indices = list(range(min(3, n)))
            examples = ", ".join(f"waypoint {i}" for i in example_indices)
            msg = (
                f"{base} "
                f"I have {n} saved waypoint{'s' if n != 1 else ''}, numbered 0 to {n - 1}. "
                f"You can say things like 'take me to {examples}'. "
            )
            if tours:
                msg += (
                    f"I also know {'these tours' if len(tours) > 1 else 'this tour'}: "
                    f"{', '.join(tours)}. "
                    f"Just say 'start tour {tours[0]}' to begin."
                )
        else:
            msg = (
                f"{base} "
                f"I know {n} waypoint{'s' if n != 1 else ''}, numbered 0 to {n - 1}. "
                "Try asking by waypoint number — for example, 'go to waypoint 2'."
            )

        self.status.task_state = TaskState.IDLE
        self._say(msg)

    # ------------------------------------------------------------------
    # Single-destination navigation (navigate intent)
    # ------------------------------------------------------------------

    def _navigate_to_pending_goal(self) -> NodeStatus:
        if self.nav_in_progress:
            return NodeStatus.RUNNING

        if self.pending_goal_pose is not None:
            x, y, label = self.pending_goal_pose
            if self._send_nav_goal(x, y, label):
                self.pending_goal_pose = None
                return NodeStatus.RUNNING
            return NodeStatus.FAILURE

        # No pose resolved — intent handler already notified the user
        self.status.task_state = TaskState.IDLE
        return NodeStatus.FAILURE

    def _send_nav_goal(self, x: float, y: float, label: str = "") -> bool:
        if not self.nav_client.server_is_ready():
            self.get_logger().warning("Nav2 action server not ready.")
            return False
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = "map"
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.w = 1.0
        self.nav_request_token += 1
        token = self.nav_request_token
        self.nav_in_progress = True
        self.status.task_state = TaskState.NAVIGATING
        self.status.current_target = label
        self._set_expression(RobotExpression.NAVIGATING)
        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(
            lambda f, t=token: self._nav_goal_response(f, t)
        )
        return True

    def _nav_goal_response(self, future, token: int):
        if token != self.nav_request_token or self.status.task_state != TaskState.NAVIGATING:
            try:
                gh = future.result()
                if gh and gh.accepted:
                    gh.cancel_goal_async()
            except Exception:
                pass
            return
        gh = future.result()
        if gh is None or not gh.accepted:
            self.nav_in_progress = False
            self.status.task_state = TaskState.IDLE
            self._set_expression(RobotExpression.IDLE)
            self._say("Navigation goal was rejected.")
            return
        self.nav_goal_handle = gh
        self.nav_result_future = gh.get_result_async()
        self.nav_result_future.add_done_callback(
            lambda f, t=token: self._nav_result(f, t)
        )

    def _nav_result(self, future, token: int):
        if token != self.nav_request_token:
            return
        self.nav_in_progress = False
        self.nav_goal_handle = None
        result = future.result()
        status = getattr(result, "status", None)
        self._set_expression(RobotExpression.IDLE)
        if status == GoalStatus.STATUS_SUCCEEDED:
            self._nav_fail_count = 0
            self._say("I've arrived at the destination.")
        elif status == GoalStatus.STATUS_CANCELED:
            self._say("Navigation was canceled.")
        else:
            self._say("Navigation finished.")
        self.status.task_state = TaskState.IDLE
        self.status.current_target = ""

    def _cancel_nav_goal(self):
        self.nav_request_token += 1
        self.pending_goal_location = ""
        self.pending_goal_pose = None
        self.nav_in_progress = False
        if self.nav_goal_handle is not None:
            self.nav_goal_handle.cancel_goal_async()
            self.nav_goal_handle = None

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _say(self, text: str):
        if not text:
            return
        self.response_pub.publish(String(data=text))
        self._set_expression(RobotExpression.TALKING)
        self.get_logger().info(f"[ARIA] {text}")

    def _publish_status(self):
        payload = json.loads(self.status.to_json())
        payload["current_tour"] = self._current_tour_name
        # Include DB summary so LLM knows what it can navigate to
        n = len(self._wp_cache)
        payload["available_waypoints"] = (
            [f"waypoint {i}" for i in range(n)] if n > 0 else []
        )
        payload["available_tours"] = self._list_available_tours()
        payload["waypoint_count"] = n
        self.status_pub.publish(String(data=json.dumps(payload)))


def main(args=None):
    rclpy.init(args=args)
    node = BehaviorTreeOrchestrator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
