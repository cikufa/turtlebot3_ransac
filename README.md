# RANSAC

***This activity is to be done as individuals, not with partners nor with teams.***

### How to get started →

Begin by reading this entire writeup and making sure you have a good understanding of it. Next, spend a good amount of time, maybe an entire day, planning and sketching out on paper how you’re going to solve this assignment. You should aim on identifying what features you need to implement, which ROS nodes and topics you’ll need and how you’ll test and evaluate your package.

# Introduction

---

In this activity, you will implement a Line-Fitting algorithm using RANSAC. The problem is, given a set of points in 2D, the goal is to find the parameters that describe the line so as to best fit the set of 2D
points. The RANSAC algorithm is a technique to estimate parameters of a model by random sampling of observed data. Given a dataset whose data elements contain both inliers and outliers, RANSAC uses the voting scheme to find the optimal fitting result. Data elements in the dataset are used to vote for one or multiple models. 

# Activity Information

---

### Objectives

- Understand how sensors work in ROS2
- Learn how to process LiDAR data
- Learn to manipulate laser scan to Cartesian co-ordinates for computation
- Implement RANSAC to perform model estimation

### Resources

- [RVIZ Markers Tutorial](https://docs.ros.org/en/humble/Tutorials/Intermediate/RViz/Marker-Display-types/Marker-Display-types.html)
- [RANSAC](https://www.cse.psu.edu/~rtc12/CSE486/lecture15.pdf)
- [Distance of point to line](https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points)
- [ROS2 Params](https://docs.ros.org/en/foxy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Parameters/Understanding-ROS2-Parameters.html)
- [`rclpy` params](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Using-Parameters-In-A-Class-Python.html#write-the-python-node)

### Requirements

- Your package should build when simply dropped into a workspace and compiled using `colcon build`
- Your launch file should launch the simulator and the RANSAC rviz config
- Your package, nodes and launch files should follow the naming convention, if your code does not work due to the filenames being incorrect, you will receive zero points

### What we provide

- Demo python/launch/config/rviz files to setup a rviz marker publisher
- RANSAC parameters yaml file


### What to submit

You must submit a ROS package with the follow file structure

```bash
turtlebot3_ransac/
├── ransac
│   ├── config
│   │   ├── demo.yaml
│   │   └── ransac.yaml
│   ├── launch
│   │   ├── demo.launch.py
│   │   └── ransac.launch.py
│   ├── package.xml
│   ├── ransac
│   │   ├── demo.py
│   │   ├── __init__.py
│   │   └── ransac.py
│   ├── resource
│   │   └── ransac
│   ├── rviz
│   │   ├── demo.rviz
│   │   └── ransac.rviz
│   ├── setup.cfg
│   └── setup.py
└── README.md
```

*Please make sure you adhere to the structure above, if your package doesn’t match it the grader will give you a **zero***

### Grading considerations

- **Late submissions:** Carefully review the course policies on submission and late assignments. Verify before the deadline that you have submitted the correct version.
- **Environment, names, and types:** You are required to adhere to the names and types of the functions and modules specified in the release code. Otherwise, your solution will receive minimal credit.

### Demo Visualization Template
```python
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
```

### Part 1 : RANSAC

---
<p align="center">
          <img width="600" height="600" src="media/ransac.svg">
</p>

RANSAC parameters
```yaml
viz_topic: /ransac_markers # Topic to publish the visualization markers
trials: 10 # Number of trials to run (N in the RANSAC algorithm)
distance_threshold: 0.1 # Distance below which a point is considered as an inlier (d_th in the RANSAC algorithm)
remain_ratio: 0.05 # Ratio of the remaining points from the start of the trials (r_rem in the RANSAC algorithm)
```

Your RANSAC node will
- Subscribe to the `/scan` topic to receive `sensor_msgs/LaserScan` messages.
- Process the incoming laser scan data using the RANSAC algorithm to extract a set of lines representing the scan
- Publish the detected lines as visualization markers on the topic specified in the YAML configuration files

The `ransac.launch` file should:
- Start Stage 2 of the TurtleBot3 Gazebo simulation
- Launch rviz with a custom configuration file to visualize the lines
- Start the RANSAC node for line extraction





>**RANSAC is an iterative algorithm and thus can have slow implementations. You can check the rate of your marker publisher using `rostopic hz /ransac_markers`. You should be getting rates > 2Hz**


### Demonstration Video
Link: https://youtu.be/zXQacqlacz4


# Submission and Assessment

---

Submit using the Github upload feature on [autolab](https://autolab.cse.buffalo.edu)

**Note: Make sure your code complies to all instructions, especially the naming conventions. Failure to comply will result in zero credit**

You will be graded on the following. Penalties are listed under each point, absolute values, w.r.t assignment total.

1. Part 1 (RANSAC) [100%] 
    1. If the simulation is not launched [-20%]
    2. If your launch file doesn’t launch rviz with the correct config [-20%]
    3. If there are consistently bad lines [-30%]