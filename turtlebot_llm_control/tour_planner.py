"""
Tour Planner
============
Interactive tool that:
1. Fetches all saved waypoints from social_guide's tour_retrieve service
2. Subscribes to /map for the occupancy grid
3. Displays a matplotlib window: map + numbered waypoint dots
4. Prompts the user to select waypoints in tour order with optional descriptions
5. Saves the result as a CSV file in ~/tours/ (or a custom directory)

Usage:
  ros2 run tour_maker tour_planner [--tours-dir ~/tours]
  ros2 run tour_maker tour_planner --tours-dir /path/to/tours
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped

try:
    from social_robot_interfaces.srv import Tours as ToursSrv
    _SRV_OK = True
except ImportError:
    _SRV_OK = False


class TourPlanner(Node):
    def __init__(self, tours_dir: str):
        super().__init__("tour_planner")
        self.tours_dir = Path(tours_dir).expanduser()
        self.tours_dir.mkdir(parents=True, exist_ok=True)

        self._map_data: OccupancyGrid | None = None
        self._waypoints: list[PoseStamped] = []

        self._map_sub = self.create_subscription(
            OccupancyGrid, "/map", self._map_cb, 10
        )

        self._tour_client = None
        if _SRV_OK:
            self._tour_client = self.create_client(ToursSrv, "tour_retrieve")
        else:
            self.get_logger().warning(
                "social_robot_interfaces not available — cannot fetch waypoints from DB"
            )

    def _map_cb(self, msg: OccupancyGrid):
        if self._map_data is None:
            self._map_data = msg
            self.get_logger().info("Map received.")

    def wait_for_map(self, timeout: float = 10.0) -> bool:
        deadline = time.time() + timeout
        while self._map_data is None and time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.2)
        return self._map_data is not None

    def fetch_waypoints(self) -> bool:
        if self._tour_client is None:
            return False
        if not self._tour_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().warning("tour_retrieve service not available")
            return False
        req = ToursSrv.Request()
        req.idx = 0
        future = self._tour_client.call_async(req)
        deadline = time.time() + 5.0
        while not future.done() and time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
        if future.done():
            self._waypoints = list(future.result().tour)
            self.get_logger().info(f"Fetched {len(self._waypoints)} waypoints.")
            return True
        return False

    # ------------------------------------------------------------------
    # Visualization
    # ------------------------------------------------------------------

    def show_map(self):
        """Render the occupancy grid + waypoints in a matplotlib window."""
        try:
            import matplotlib
            matplotlib.use("TkAgg")
        except Exception:
            try:
                import matplotlib
                matplotlib.use("Qt5Agg")
            except Exception:
                pass

        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("ERROR: matplotlib/numpy not installed. Run: pip install matplotlib numpy")
            return None, None

        fig, ax = plt.subplots(figsize=(12, 10))
        fig.suptitle("Tour Planner — Social Tour Guide Robot", fontsize=14, fontweight="bold")

        if self._map_data is not None:
            w = self._map_data.info.width
            h = self._map_data.info.height
            res = self._map_data.info.resolution
            ox = self._map_data.info.origin.position.x
            oy = self._map_data.info.origin.position.y

            grid = np.array(self._map_data.data, dtype=np.int8).reshape((h, w))
            display = np.zeros((h, w), dtype=np.uint8)
            display[grid == -1] = 128   # unknown → gray
            display[grid == 0] = 255    # free → white
            display[grid == 100] = 0    # occupied → black

            extent = [ox, ox + w * res, oy, oy + h * res]
            ax.imshow(display, cmap="gray", origin="lower",
                      extent=extent, vmin=0, vmax=255, alpha=0.85)
        else:
            ax.text(0.5, 0.5, "No map available\n(showing waypoints only)",
                    transform=ax.transAxes, ha="center", va="center", fontsize=12, color="gray")

        for i, wp in enumerate(self._waypoints):
            x, y = wp.pose.position.x, wp.pose.position.y
            ax.plot(x, y, "ro", markersize=12)
            ax.text(x + 0.05, y + 0.05, str(i), fontsize=9,
                    color="darkred", fontweight="bold")

        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        n = len(self._waypoints)
        ax.set_title(f"{n} waypoints (indices 0–{n-1})" if n else "No waypoints saved yet")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.5)
        return fig, ax

    def _highlight_route(self, fig, ax, indices: list[int]):
        """Draw the selected route on the existing figure."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            return
        xs = [self._waypoints[i].pose.position.x for i in indices]
        ys = [self._waypoints[i].pose.position.y for i in indices]
        ax.plot(xs, ys, "b-", linewidth=2, alpha=0.7)
        for order, (idx, x, y) in enumerate(zip(indices, xs, ys)):
            ax.plot(x, y, "bs", markersize=14, alpha=0.4)
            ax.text(x - 0.12, y - 0.18, str(order + 1),
                    fontsize=8, color="blue", fontweight="bold")
        plt.draw()
        plt.pause(0.5)

    # ------------------------------------------------------------------
    # Interactive tour builder
    # ------------------------------------------------------------------

    def build_tour(self, fig, ax) -> tuple[list[int], list[str], str]:
        """Prompt user to select waypoints and descriptions, return (indices, descs, name)."""
        n = len(self._waypoints)
        print("\n" + "=" * 60)
        print("  TOUR BUILDER")
        print("=" * 60)
        if n == 0:
            print("  No waypoints in the database.")
            print("  Drive the robot with teleop and use waypoint_recorder first.")
            print("=" * 60)
            return [], [], ""

        print(f"  {n} waypoints available (indices 0 to {n-1})\n")
        for i, wp in enumerate(self._waypoints):
            x, y = wp.pose.position.x, wp.pose.position.y
            print(f"    [{i:3d}]  x={x:7.3f}  y={y:7.3f}")

        print()
        print("  Enter waypoint indices in the order you want the tour to visit them.")
        print("  Example:  3 1 7 2 5   (visits 3 first, then 1, then 7, etc.)")
        print()

        while True:
            raw = input("  Tour order: ").strip()
            try:
                indices = [int(x) for x in raw.split()]
            except ValueError:
                print("  Please enter space-separated numbers only.\n")
                continue
            if not indices:
                print("  Please enter at least one waypoint index.\n")
                continue
            bad = [i for i in indices if not (0 <= i < n)]
            if bad:
                print(f"  Invalid indices: {bad} — must be in 0–{n-1}.\n")
                continue
            break

        print()
        print("  Add a description for each stop (what ARIA says on arrival).")
        print("  Press Enter to leave a stop silent.\n")
        descriptions = []
        for idx in indices:
            wp = self._waypoints[idx]
            x, y = wp.pose.position.x, wp.pose.position.y
            desc = input(f"  Stop at waypoint {idx} ({x:.2f}, {y:.2f}): ").strip()
            descriptions.append(desc)

        # Auto-name
        existing = sorted(self.tours_dir.glob("tour*.csv"))
        next_num = len(existing) + 1
        print()
        name_raw = input(f"  Tour name [tour{next_num}]: ").strip()
        name = name_raw if name_raw else f"tour{next_num}"

        # Highlight on map
        if fig is not None and self._waypoints:
            self._highlight_route(fig, ax, indices)

        return indices, descriptions, name

    # ------------------------------------------------------------------
    # CSV save
    # ------------------------------------------------------------------

    def save_csv(self, indices: list[int], descriptions: list[str], name: str) -> str:
        path = self.tours_dir / f"{name}.csv"
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([f"# tour: {name}"])
            writer.writerow([f"# saved: {datetime.now().isoformat()}"])
            writer.writerow([f"# waypoints: {len(indices)}"])
            for idx, desc in zip(indices, descriptions):
                writer.writerow([idx, desc])
        print(f"\n  ✓ Tour saved to: {path}")
        print(f"    Start with voice: \"start tour {name}\"")
        return str(path)


def main(args=None):
    parser = argparse.ArgumentParser(description="Tour Planner for Social Tour Guide Robot")
    parser.add_argument(
        "--tours-dir", default="~/tours",
        help="Directory to save tour CSV files (default: ~/tours)"
    )
    known, ros_args = parser.parse_known_args()

    rclpy.init(args=ros_args or args)
    node = TourPlanner(tours_dir=known.tours_dir)

    print("\nFetching waypoints from database…")
    if not node.fetch_waypoints():
        print("WARNING: Could not fetch waypoints from tour_retrieve service.")
        print("         Make sure social_guide nodes are running.")

    print("Waiting for map…")
    if not node.wait_for_map(timeout=10.0):
        print("WARNING: Map not received within 10 s. Will show waypoints only.")

    fig, ax = node.show_map()
    indices, descriptions, name = node.build_tour(fig, ax)

    if indices:
        node.save_csv(indices, descriptions, name)

    try:
        import matplotlib.pyplot as plt
        input("\n  Press Enter to close the map window…")
        plt.close("all")
    except Exception:
        pass

    node.destroy_node()
    rclpy.shutdown()
