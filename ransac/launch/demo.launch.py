import os

from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetParameter

def generate_launch_description():
    declare_viz_topic_cmd = DeclareLaunchArgument(
        "viz_topic", default_value="/ransac_demo_markers",
        description="Topic to publish visualization markers to",
    )

    declare_line_list_cmd = DeclareLaunchArgument(
        "line_list", default_value="[]",
        description="List of lines to visualize, each line is represented as [x1,y1,x2,y2]",
    )

    pkg_share = get_package_share_directory("ransac")
    config_file = os.path.join(pkg_share, "config", "demo.yaml")
    
    demo_node = Node(
        package="ransac",
        executable="demo",
        name="demo",
        parameters=[config_file,],
        output="screen",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", os.path.join(pkg_share, "rviz", "demo.rviz")],
        output="screen",
    )

    return LaunchDescription([
        declare_viz_topic_cmd,
        declare_line_list_cmd,
        demo_node,
        rviz_node,
    ])
