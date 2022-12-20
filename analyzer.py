from rospy_message_converter import message_converter # Used for converting ROS messaged to Python dictionaries
from pathlib import Path
from pathlib import PurePath
from termcolor import colored
import argparse
import os
import rosbag
import yaml
import csv
import paramiko

def analyzer_arg_parser():
     # Create a parser object to handle commandline input
    parser = argparse.ArgumentParser(description="Rosbag Analyzer", epilog="If you have propositions for other flags,\nfeel free to create an issue on GitHub!\nMaintainer: S.Piasecki")

    groupFileDir = parser.add_mutually_exclusive_group(required=True)
    groupFileDir.add_argument('-d', type=str, help="Takes an absolute path to a directory and loads all rosbags within it be analysed", default="")
    parser.add_argument('-r', type=str, help="The directory with rosbags is filtered recursively (entire file tree starting at given path is analysed). WARNING - can be very slow!")

    parser.add_argument('--nas-load', action='store_true', help="Load files to analyse from the NAS")
    parser.add_argument('--nas-upload', action='store_true', help="Upload result to the NAS")

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
    accumulatorDict = { "xVelAvg": 0.0, "yVelAvg": 0.0, "laps": 0 } # Add more accumulators if required
    msgTopics = ["/can_msgs/velocity_estimation", "/common/lap_counter"] # Add more topics if required

    velMsgCounter = 0
    for topic, msg, t in rosbag.Bag(filename, 'r').read_messages(topics=msgTopics):
        msgDict = message_converter.convert_ros_message_to_dictionary(msg)

        if topic == "/can_msgs/velocity_estimation":
            accumulatorDict["xVelSum"] += msgDict["vel"]["x"]
            accumulatorDict["yVelSum"] += msgDict["vel"]["y"]
            velMsgCounter += 1

        if topic == "/common/lap_counter":
            accumulatorDict["laps"] += msgDict["data"]

    accumulatorDict["xVelSum"] /= velMsgCounter
    accumulatorDict["yVelSum"] /= velMsgCounter

    return accumulatorDict

def ssh_to_nas():
    sshClient = paramiko.SSHClient()
    sshClient.load_system_host_keys()
    sshClient.connect('mavt-amz-nas1.ethz.ch', username='amz', password='CarbonKurt33')
    stdin, stdout, stderr = sshClient.exec_command('cd .. \n cd amz-nas \n ls')
    lines = stdout.readlines()
    # TODO: after SSHing execute the appropriate commands depending on user input

def is_rosbag(path):
    file_name, file_extension = os.path.splitext(path)

    if not os.path.isfile(path):
        return False
    if file_extension != '.bag' and file_extension != '.bag'
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
        fullObjPath = absoluteDirName + '/' + objName
        if is_rosbag(fullObjPath):
            # TODO: analyse the rosbag file (put everything in try/raise to forward exceptions)
            with open(analysisFileName, 'w', encoding='UTF-8') as f:
                writer = csv.writer(f)

                # 1) If analysis file is empty - add header
                if os.stat(analysisFileName).st_size == 0:
                    header = ['file_name', 'per', 'est', 'con', 'vel', 'laps', 'dur']
                    writer.writerow(header)

                # 2) add row corresponding to current file to CSV

                # 3) inform the user via standard output that file was succesfully analysed
        elif os.path.isdir(fullObjPath) and isRecursive:
            analyse_dir_content(fullObjPath, isRecursive)
        else:
            print(colored(f'Ignoring {fullObjPath}: it is not a rosbag or directory!', 'cyan'))

def main(args):
    # Check the path which user gave as input
    assert not args.d == "", f"The script requires the path of the directory to analyse as parameter!"
    assert os.path.isdir(args.d), f"The passed directory does not exist!"

    analyse_dir_content(args.d, args.r)

if __name__ == "__main__":
    args = analyzer_arg_parser()
    main(args)