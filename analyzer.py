from rospy_message_converter import message_converter # Used for converting ROS messaged to Python dictionaries
from pathlib import Path
from pathlib import PurePath
import os
import rosbag
import argparse
import yaml
import paramiko

def arg_parser():
    # Create a parser object to handle commandline input
    parser = argparse.ArgumentParser(description="Rosbag Analyzer", epilog="If you have propositions for other flags,\nfeel free to create an issue on GitHub!\nMaintainer: S.Piasecki")

    # Add the different parser arguments
    # TODO: Add help messages!
    parser.add_argument('--per', action='store_true', help="")
    parser.add_argument('--est', action='store_true', help="")
    parser.add_argument('--con', action='store_true', help="")

    parser.add_argument('-v', action='store_true', default=True, help="")
    parser.add_argument('-c', action='store_true', help="")
    parser.add_argument('-l', default=60, help="")

    group_file_dir = parser.add_mutually_exclusive_group(required=True)
    group_file_dir.add_argument('-f', type=str)
    group_file_dir.add_argument('-r', type=str)

    group_nas = parser.add_mutually_exclusive_group(required=False)
    group_nas.add_argument('--nas-load', action='store_true')
    group_nas.add_argument('--nas-upload', action='store_true')

    args = parser.parse_args()
    return args

def check_module_freq(filename, args):
    # Read rosbag info
    topic_info_dict = yaml.safe_load(rosbag.Bag(filename, 'r')._get_yaml_info())["topics"]

    # TODO: should the user need to specify how many Hz he needs?
    return_dict = { "per": True, "est": True, "con": True }
    for topic_obj in topic_info_dict:
        topic_module = topic_obj["topic"].split(os.path.sep)[1]
        topic_freq = topic_obj["frequency"]
        if args.per and topic_module is "perception" and topic_freq < 9:
            return_dict["per"] = False
        if args.est and topic_module is "estimation" and topic_freq < 9: # Adapt! Estimation is edge case! Has messages with extra low frequency!
            return_dict["est"] = False
        if args.con and topic_module is "control" and topic_freq < 9:
            return_dict["con"] = False

    return return_dict

def ssh_to_nas():
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.connect('mavt-amz-nas1.ethz.ch', username='amz', password='CarbonKurt33')
    stdin, stdout, stderr = ssh_client.exec_command('cd .. \n cd amz-nas \n ls')
    lines = stdout.readlines()
    # TODO: after sshing execute the appropriate commands depending on user input

def check_properties(filename, args):
    counters_dict = { "vel_counter": 0, "lap_counter": 0 } # Add more counters based on flags
    msg_topics = ["/can_msgs/velocity_estimation", "/common/lap_counter"] # Add more counters based on flags

    # TODO: implement similar logic as for check_module_frequency
    for topic, msg, t in rosbag.Bag(filename, 'r').read_messages(topics=msg_topics):
        msg_dict = message_converter.convert_ros_message_to_dictionary(msg)

        # Increment vel_counter if velocity is message is not 0
        if topic == "/can_msgs/velocity_estimation" and (msg_dict["vel"]["x"] > 0.0 or msg_dict["vel"]["y"] > 0.0):
            counters_dict["vel_counter"] += 1

        # Increment lap_counter if lap is message is not 0
        if topic == "/common/lap_counter" and msg_dict["data"] != 0:
            counters_dict["lap_counter"] += 1

    print(counters_dict)

if __name__ == "__main__":
    args = arg_parser()
