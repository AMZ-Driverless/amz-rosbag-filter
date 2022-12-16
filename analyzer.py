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
    parser.add_argument('--per', action='store_true', help="Filter for rosbags where perception runs at ~10 Hz")
    parser.add_argument('--est', action='store_true', help="Filter for rosbags where estimation runs at ~10 Hz")
    parser.add_argument('--con', action='store_true', help="Filter for rosgags where control runs at ~10 Hz")

    parser.add_argument('-v', action='store_true', default=True, help="Filter for rosbag where the car moves")
    parser.add_argument('-c', default=0, help="Filter for rosbags where car does at least X laps")
    parser.add_argument('-l', default=60, help="Filter for rosbags which are at least x seconds long")

    group_file_dir = parser.add_mutually_exclusive_group(required=True)
    group_file_dir.add_argument('-f', type=str, help="Takes an absolute path and loads a single rosbag file (local/NAS)")
    group_file_dir.add_argument('-r', type=str, help="Takes an absolute path to a directory and loads all rosbags within it be analysed (recursive + local/NAS). WARNING - can be very slow!")

    group_nas = parser.add_mutually_exclusive_group(required=False)
    group_nas.add_argument('--nas-load', action='store_true', help="Load file/directory from the NAS")
    group_nas.add_argument('--nas-upload', action='store_true', help="Upload filtered rosbags to the NAS")

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
        if args.per and topic_module == "perception" and topic_freq < 9:
            return_dict["per"] = False
        if args.est and topic_module == "estimation" and topic_freq < 9: # Adapt! Estimation is edge case! Has messages with extra low frequency!
            return_dict["est"] = False
        if args.con and topic_module == "control" and topic_freq < 9:
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
    counters_dict = { "vel_counter": 0, "lap_counter": 0 } # Add more counters if required
    msg_topics = ["/can_msgs/velocity_estimation", "/common/lap_counter"] # Add more topics if required

    # TODO: implement similar logic as for check_module_frequency
    for topic, msg, t in rosbag.Bag(filename, 'r').read_messages(topics=msg_topics):
        msg_dict = message_converter.convert_ros_message_to_dictionary(msg)

        if args.v and topic == "/can_msgs/velocity_estimation" and (msg_dict["vel"]["x"] > 0.0 or msg_dict["vel"]["y"] > 0.0):
            counters_dict["vel_counter"] += 1

        if args.c and topic == "/common/lap_counter" and msg_dict["data"] == args.c:
            counters_dict["lap_counter"] += 1
    
    return_dict = { "vel": True, "lap": True } # Add more return values if necessary

    if counters_dict["vel_counter"] < 50 and args.v:
        return_dict["vel"] = False

    if counters_dict["lap_counter"] == 0 and args.c:
        return_dict["lap"] = False

    return return_dict

if __name__ == "__main__":
    args = arg_parser()
