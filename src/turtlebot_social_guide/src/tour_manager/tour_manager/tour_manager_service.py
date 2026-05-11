import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from social_robot_interfaces.srv import Tours

from tour_manager.tour_database import load_waypoints, resolve_db_path


class TourManager(Node):

    def __init__(self):
        super().__init__("tour_manager")
        self.get_logger().info("Initializing tour manager")
        self.declare_parameter("db_path", "")
        self.db_path = str(self.get_parameter("db_path").value or "")
        self.srv = self.create_service(
            Tours, "tour_retrieve", self.tour_retrieve_callback
        )
        self.subscription_ = self.create_subscription(
            PoseStamped,
            "save_tour",
            self.save_tour_callback,
            10,
        )
        self.get_logger().info(
            "Using tour database at %s" % resolve_db_path(self.db_path)
        )

    def tour_retrieve_callback(self, request, response):
        tour_obj = self.retrieve_tour(request.idx)
        list_ = []
        for i in tour_obj:
            waypoint = PoseStamped()
            waypoint.header.frame_id = "map"
            waypoint.pose.position.x = i[0]
            waypoint.pose.position.y = i[1]
            waypoint.pose.position.z = i[2]
            waypoint.pose.orientation.x = i[3]
            waypoint.pose.orientation.y = i[4]
            waypoint.pose.orientation.z = i[5]
            waypoint.pose.orientation.w = i[6]
            list_.append(waypoint)
        response.tour = list_
        return response

    def save_tour_callback(self, msg):
        self.add_point(msg)

    def add_point(self, x: PoseStamped):
        import sqlite3

        resolved_db = resolve_db_path(self.db_path)
        resolved_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(resolved_db)) as connection:
            cur = connection.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS tours (px,py,pz,qx,qy,qz,qw)")
            cur.execute(
                "INSERT INTO tours VALUES (?,?,?,?,?,?,?)",
                (
                    x.pose.position.x,
                    x.pose.position.y,
                    x.pose.position.z,
                    x.pose.orientation.x,
                    x.pose.orientation.y,
                    x.pose.orientation.z,
                    x.pose.orientation.w,
                ),
            )
            connection.commit()
        self.get_logger().info("Saved 1 new waypoint into tour")

    def retrieve_tour(self, idx):
        return load_waypoints(self.db_path)


def main(args=None):
    rclpy.init(args=args)

    tour_manager = TourManager()

    rclpy.spin(tour_manager)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
