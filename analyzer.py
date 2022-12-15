from rospy_message_converter import message_converter # Used for converting ROS messaged to Python dictionaries
import rosbag
import sys
import yaml

def main(argv):
    # Read rosbag info
    info_dict = yaml.safe_load(rosbag.Bag(argv[0], 'r')._get_yaml_info())
    # TODO: make decisions based on rosbag info - what is running at how many Hz?

    counters_dict = { "vel_counter": 0, "lap_counter": 0 } # Add more counters based on flags
    msg_topics = ["/can_msgs/velocity_estimation", "/common/lap_counter"] # Add more counters based on flags

    for topic, msg, t in rosbag.Bag(argv[0], 'r').read_messages(topics=msg_topics):
        msg_dict = message_converter.convert_ros_message_to_dictionary(msg)

        # Increment vel_counter if velocity is message is not 0
        if topic == "/can_msgs/velocity_estimation" and (msg_dict["vel"]["x"] > 0.0 or msg_dict["vel"]["y"] > 0.0):
            counters_dict["vel_counter"] += 1

        # Increment lap_counter if lap is message is not 0
        if topic == "/common/lap_counter" and msg_dict["data"] != 0:
            counters_dict["lap_counter"] += 1

    print(counters_dict)

if __name__ == "__main__":
    # Pass command line arguments to the main function
    main(sys.argv[1:])