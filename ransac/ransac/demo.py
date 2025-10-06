#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
import yaml
import numpy as np

class MarkerPublisher(Node):
    def __init__(self):
        super().__init__("marker_publisher")
        self.declare_parameter("viz_topic", "/ransac_demo_markers") # declaration of the parameter with a default value
        self.marker_topic = self.get_parameter("viz_topic").get_parameter_value().string_value  # get the topic name from the parameter server
        self.declare_parameter("line_list", "[]") # declaration of the parameter with a default value
        self.line_list = np.array(yaml.safe_load(self.get_parameter("line_list").get_parameter_value().string_value), dtype=float) # get the line list from the parameter server
        self.get_logger().info(f"Line list: {self.line_list}")
        self.marker_pub = self.create_publisher(Marker, self.marker_topic, 10)
        self.pub_timer = self.create_timer(1.0, self.publish_marker) # create a timer to publish at 1 Hz
    
    
    def publish_marker(self):
        marker = Marker()
        marker.header.frame_id = "map" # frame_id is not the same as the topic name. rviz defaults to map frame
        marker.header.stamp = rclpy.time.Time().to_msg()
        marker.ns = "line"
        marker.id = 0
        marker.type = Marker.LINE_LIST # LINE_LIST is used to draw multiple lines
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.1 # line width

        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0 
        marker.color.a = 1.0

        # self.line_list is of the form [[5,5,10,10],[-5,-5,-10,-10],[5,-5,10,-10],
        # [-5,5,-10,10],[-2,2,2,2],[2,2,2,-2],[2,-2,-2,-2],[-2,-2,-2,2]]
        for line in self.line_list:
            # lines are drawn between consecutive pairs of points
            p1 = Point()
            p1.x = line[0]
            p1.y = line[1]
            marker.points.append(p1)

            p2 = Point()
            p2.x = line[2]
            p2.y = line[3]
            marker.points.append(p2)

        self.marker_pub.publish(marker)

def main(args=None):
    rclpy.init()
    mp = MarkerPublisher()
    rclpy.spin(mp)
    mp.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
    