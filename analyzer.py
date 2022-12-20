from rospy_message_converter import message_converter # Used for converting ROS messaged to Python dictionaries
from termcolor import colored
import argparse
import os
import rosbag
import yaml
import csv
import math

def analyzer_arg_parser():
     # Create a parser object to handle commandline input
    parser = argparse.ArgumentParser(description="Rosbag Analyzer", epilog="If you have propositions for other flags,\nfeel free to create an issue on GitHub!\nMaintainer: S.Piasecki")

    groupFileDir = parser.add_mutually_exclusive_group(required=True)
    groupFileDir.add_argument('-d', type=str, help="Takes an absolute path to a directory and loads all rosbags within it be analysed", default="")
    parser.add_argument('-r', type=str, help="The directory with rosbags is filtered recursively (entire file tree starting at given path is analysed). WARNING - can be very slow!")

    args = parser.parse_args()
    return args

def check_module_freq(filename):
    # Read rosbag info
    topicInfoDict = yaml.safe_load(rosbag.Bag(filename, 'r')._get_yaml_info())["topics"]

    returnDict = { "per": True, "est": True, "con": True }
    for topicObj in topicInfoDict:
        topicModule = topicObj["topic"].split(os.path.sep)[1]
        topicFreq = topicObj.get("frequency")

        if topicModule == "perception" and (topicFreq and topicFreq < 9):
            returnDict["per"] = False
        if topicModule == "estimation" and (topicFreq and topicFreq < 9):
            returnDict["est"] = False
            # TODO: Adapt! Estimation is edge case! Has messages with extra low frequency!
            # These two have frequency although they really should not
            # /estimation/viz/boundary_selector
            # /estimation/local_map_mode
        if topicModule == "control" and (topicFreq and topicFreq < 9):
            returnDict["con"] = False

    return returnDict

def check_rosbag_properties(filename):
    accumulatorDict = { "vel": 0.0, "laps": 0 } # Add more accumulators if required
    msgTopics = ["/can_msgs/velocity_estimation", "/common/lap_counter"] # Add more topics if required

    velMsgCounter = 0
    for topic, msg, t in rosbag.Bag(filename, 'r').read_messages(topics=msgTopics):
        msgDict = message_converter.convert_ros_message_to_dictionary(msg)

        if topic == "/can_msgs/velocity_estimation":
            velX = msgDict["vel"]["x"]
            velY = msgDict["vel"]["y"]
            accumulatorDict["vel"] += math.sqrt(velX ** 2 + velY ** 2)
            velMsgCounter += 1

        if topic == "/common/lap_counter":
            accumulatorDict["laps"] += msgDict["data"]

    accumulatorDict["vel"] /= velMsgCounter

    return accumulatorDict

def is_rosbag(path):
    file_name, file_extension = os.path.splitext(path)

    if not os.path.isfile(path):
        return False
    if file_extension != '.bag' and file_extension != '.active':
        return False

    return True

def analyse_dir_content(absoluteDirName, isRecursive=False):
    # Remove existing rosbag_analysis.csv file in this directory (could be outdated)
    analysisFileName = absoluteDirName + 'rosbag_analysis.csv'
    if os.path.isfile(analysisFileName):
        os.remove(analysisFileName)
        print(colored(f'Removing {analysisFileName}: a new analysis file will be created for the directory.', 'cyan'))

    # Analysis
    for objName in os.listdir(absoluteDirName):
        absoluteObjPath = f'{absoluteDirName}/{objName}'
        if is_rosbag(absoluteObjPath):
            # TODO: analyse the rosbag file (put everything in try/raise to forward exceptions)
            with open(analysisFileName, 'w', encoding='UTF-8') as f:
                writer = csv.writer(f)

                # 1) If analysis file is empty - add header
                if os.stat(analysisFileName).st_size == 0:
                    header = ['file_name', 'per', 'est', 'con', 'vel', 'laps', 'dur']
                    writer.writerow(header)

                # 2) add row corresponding to current file to CSV

                # 3) inform the user via standard output that file was succesfully analysed
        elif os.path.isdir(absoluteObjPath) and isRecursive:
            analyse_dir_content(absoluteObjPath, isRecursive)
        else:
            print(colored(f'Ignoring {absoluteObjPath}: it is not a rosbag or directory!', 'cyan'))

def main(args):
    # Check the path which user gave as input
    assert not args.d == "", f"The script requires the path of the directory to analyse as parameter!"
    assert os.path.isdir(args.d), f"The passed directory does not exist!"

    analyse_dir_content(args.d, args.r)

if __name__ == "__main__":
    args = analyzer_arg_parser()
    main(args)