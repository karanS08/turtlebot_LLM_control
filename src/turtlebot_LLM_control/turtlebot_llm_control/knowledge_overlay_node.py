from __future__ import annotations

import rclpy
from geometry_msgs.msg import Point
from nav_msgs.msg import OccupancyGrid
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import ColorRGBA
from visualization_msgs.msg import Marker, MarkerArray

from turtlebot_llm_control.knowledge_store import KnowledgeStore, resolve_knowledge_db_path


class KnowledgeOverlayNode(Node):
    def __init__(self):
        super().__init__("knowledge_overlay_node")
        self.declare_parameter("knowledge_db_path", "")
        self.declare_parameter("map_topic", "/map")
        self.declare_parameter("marker_topic", "/knowledge_markers")

        self.knowledge_db_path = str(self.get_parameter("knowledge_db_path").value or "")
        self.map_topic = str(self.get_parameter("map_topic").value or "/map")
        self.marker_topic = str(self.get_parameter("marker_topic").value or "/knowledge_markers")

        self.store = KnowledgeStore(self.knowledge_db_path)
        qos = QoSProfile(
            depth=1,
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.publisher = self.create_publisher(MarkerArray, self.marker_topic, qos)
        self.map_subscription = self.create_subscription(
            OccupancyGrid, self.map_topic, self.handle_map, 10
        )
        self.timer = self.create_timer(2.0, self.publish_overlay)
        self.map_frame = "map"
        self.map_stamp = None
        self.get_logger().info(
            "Knowledge overlay ready. DB=%s topic=%s"
            % (resolve_knowledge_db_path(self.knowledge_db_path), self.marker_topic)
        )

    def handle_map(self, msg: OccupancyGrid) -> None:
        self.map_frame = msg.header.frame_id or "map"
        self.map_stamp = msg.header.stamp
        self.publish_overlay()

    def publish_overlay(self) -> None:
        if self.map_stamp is None:
            return

        entries = self.store.list_entries()
        marker_array = MarkerArray()
        marker_array.markers.append(self.make_clear_marker())
        next_id = 1
        for entry in entries:
            x, y, yaw = self.store.resolve_position(entry)
            if x is None or y is None:
                continue
            color = self.color_for_kind(entry.kind)
            marker_array.markers.append(
                self.make_point_marker(entry, next_id, x, y, 0.0, color)
            )
            next_id += 1
            marker_array.markers.append(
                self.make_label_marker(entry, next_id, x, y, 0.0)
            )
            next_id += 1

        self.publisher.publish(marker_array)

    def make_clear_marker(self) -> Marker:
        marker = Marker()
        marker.header.frame_id = self.map_frame
        marker.header.stamp = self.map_stamp
        marker.action = Marker.DELETEALL
        return marker

    def make_point_marker(self, entry, marker_id, x, y, z, color) -> Marker:
        marker = Marker()
        marker.header.frame_id = self.map_frame
        marker.header.stamp = self.map_stamp
        marker.ns = "knowledge_points"
        marker.id = marker_id
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = z
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.22
        marker.scale.y = 0.22
        marker.scale.z = 0.22
        marker.color = color
        return marker

    def make_label_marker(self, entry, marker_id, x, y, z) -> Marker:
        marker = Marker()
        marker.header.frame_id = self.map_frame
        marker.header.stamp = self.map_stamp
        marker.ns = "knowledge_labels"
        marker.id = marker_id
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = z + 0.28
        marker.pose.orientation.w = 1.0
        marker.scale.z = 0.18
        marker.color = ColorRGBA(r=1.0, g=1.0, b=1.0, a=0.95)
        marker.text = entry.title
        return marker

    @staticmethod
    def color_for_kind(kind: str) -> ColorRGBA:
        kind = (kind or "page").strip().lower()
        if kind == "artifact":
            return ColorRGBA(r=1.0, g=0.55, b=0.1, a=0.95)
        if kind == "place":
            return ColorRGBA(r=0.2, g=0.6, b=1.0, a=0.95)
        if kind == "route":
            return ColorRGBA(r=0.25, g=0.9, b=0.5, a=0.95)
        return ColorRGBA(r=0.7, g=0.7, b=0.7, a=0.95)


def main(args=None):
    rclpy.init(args=args)
    node = KnowledgeOverlayNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
