from __future__ import annotations

import rclpy
from geometry_msgs.msg import Point
from nav_msgs.msg import OccupancyGrid
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import ColorRGBA
from visualization_msgs.msg import Marker, MarkerArray

from tour_manager.tour_database import load_waypoints, resolve_db_path


class WaypointVisualizer(Node):
    def __init__(self):
        super().__init__("waypoint_visualizer")
        self.declare_parameter("db_path", "")
        self.declare_parameter("map_topic", "/map")
        self.declare_parameter("waypoint_topic", "/waypoints")
        self.declare_parameter("frame_id", "map")

        self.db_path = str(self.get_parameter("db_path").value or "")
        self.map_topic = str(self.get_parameter("map_topic").value or "/map")
        self.waypoint_topic = str(
            self.get_parameter("waypoint_topic").value or "/waypoints"
        )
        self.frame_id = str(self.get_parameter("frame_id").value or "map")

        qos = QoSProfile(
            depth=1,
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.publisher = self.create_publisher(MarkerArray, self.waypoint_topic, qos)
        self.map_subscription = self.create_subscription(
            OccupancyGrid,
            self.map_topic,
            self.handle_map,
            10,
        )
        self.last_map_stamp = None
        self.get_logger().info(
            "Waypoint visualizer ready. DB=%s topic=%s"
            % (resolve_db_path(self.db_path), self.waypoint_topic)
        )

    def handle_map(self, msg: OccupancyGrid) -> None:
        if self.last_map_stamp == msg.header.stamp:
            return
        self.last_map_stamp = msg.header.stamp
        self.publish_waypoints(msg.header.frame_id or self.frame_id, msg.header.stamp)

    def publish_waypoints(self, frame_id, stamp) -> None:
        waypoints = load_waypoints(self.db_path)
        marker_array = MarkerArray()
        marker_array.markers.append(self.make_clear_marker(frame_id, stamp))
        if not waypoints:
            self.get_logger().info("No stored waypoints found to display.")
            self.publisher.publish(marker_array)
            return

        path_points = []
        for index, waypoint in enumerate(waypoints):
            x, y, z, *_orientation = waypoint
            path_points.append((x, y, z))
            marker_array.markers.append(
                self.make_sphere_marker(frame_id, stamp, index, x, y, z)
            )
            marker_array.markers.append(
                self.make_text_marker(frame_id, stamp, index, x, y, z)
            )

        marker_array.markers.append(self.make_path_marker(frame_id, stamp, path_points))
        self.publisher.publish(marker_array)
        self.get_logger().info(
            "Published %d stored waypoints to %s."
            % (len(waypoints), self.waypoint_topic)
        )

    def make_clear_marker(self, frame_id, stamp) -> Marker:
        marker = Marker()
        marker.header.frame_id = frame_id
        marker.header.stamp = stamp
        marker.action = Marker.DELETEALL
        return marker

    def make_sphere_marker(self, frame_id, stamp, index, x, y, z) -> Marker:
        marker = Marker()
        marker.header.frame_id = frame_id
        marker.header.stamp = stamp
        marker.ns = "stored_waypoints"
        marker.id = index
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = z
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.18
        marker.scale.y = 0.18
        marker.scale.z = 0.18
        marker.color = ColorRGBA(r=0.2, g=0.85, b=0.35, a=0.95)
        return marker

    def make_text_marker(self, frame_id, stamp, index, x, y, z) -> Marker:
        marker = Marker()
        marker.header.frame_id = frame_id
        marker.header.stamp = stamp
        marker.ns = "stored_waypoint_labels"
        marker.id = 1000 + index
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = z + 0.25
        marker.pose.orientation.w = 1.0
        marker.scale.z = 0.18
        marker.color = ColorRGBA(r=1.0, g=1.0, b=1.0, a=1.0)
        marker.text = "WP %d" % (index + 1)
        return marker

    def make_path_marker(self, frame_id, stamp, path_points) -> Marker:
        marker = Marker()
        marker.header.frame_id = frame_id
        marker.header.stamp = stamp
        marker.ns = "stored_route"
        marker.id = 2000
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.scale.x = 0.05
        marker.color = ColorRGBA(r=0.9, g=0.35, b=0.15, a=0.95)
        marker.points = []
        for x, y, z in path_points:
            point = Point()
            point.x = x
            point.y = y
            point.z = z
            marker.points.append(point)
        return marker


def main(args=None):
    rclpy.init(args=args)
    node = WaypointVisualizer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
