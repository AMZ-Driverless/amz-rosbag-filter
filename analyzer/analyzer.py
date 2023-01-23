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
    parser = argparse.ArgumentParser(description="ROSBag Analyzer", epilog="If you have propositions for other flags,\nfeel free to create an issue on GitHub!\nMaintainer: S.Piasecki")
    parser.add_argument('-d', type=str, help="Not optional (!)- take a relative path to a directory and analyses all ROSBags within it", required=True)
    parser.add_argument('-r', action='store_true', help="The directory passed with -d flag is searched recursively (entire file tree starting at given path is analysed). WARNING - can be very slow!")

    args = parser.parse_args()
    return args

def check_module_freq(objPath):
    # Read rosbag info
    infoDict = yaml.safe_load(rosbag.Bag(objPath, 'r')._get_yaml_info())
    # Create a list of edge cases - so topics which should be excluded from the frequency search for various reasons
    edgeCases = ['/estimation/boundary', '/estimation/viz/point_of_interest', '/estimation/viz/boundary_selector', '/estimation/local_map_mode']
    # This value is set to 9 because if something runs at (for example) 9.6 Hz, we would still like to count it as 10 Hz
    targetFreqency = 9
    returnDict = { "dur": infoDict["duration"] }

    # Iterate over all topics present in the 'rosbag info'
    for topicObj in infoDict["topics"]:
        # Check if this topic should be ignored
        if topicObj["topic"] in edgeCases:
            continue

        topicModule = topicObj["topic"].split(os.path.sep)[1]
        topicFreq = topicObj.get("frequency")

        if topicModule == "perception" and (topicFreq and topicFreq > targetFreqency):
            returnDict["per"] = True
        if topicModule == "estimation" and (topicFreq and topicFreq > targetFreqency):
            returnDict["est"] = True
        if topicModule == "control" and (topicFreq and topicFreq < targetFreqency):
            returnDict["con"] = True

    # If topic for a module never occures - mark it as False
    if not 'per' in returnDict:
        returnDict["per"] = False
    if not 'est' in returnDict:
        returnDict["est"] = False
    if not 'con' in returnDict:
        returnDict["con"] = False

    return returnDict

def check_rosbag_properties(objPath):
    accumulatorDict = { "vel": 0.0, "laps": 0 } # Add more accumulators if required
    msgTopics = ["/can_msgs/velocity_estimation", "/common/lap_counter"] # Add more topics if required

    velMsgCounter = 0
    for topic, msg, t in rosbag.Bag(objPath, 'r').read_messages(topics=msgTopics):
        msgDict = message_converter.convert_ros_message_to_dictionary(msg)

        if topic == "/can_msgs/velocity_estimation":
            velX = msgDict["vel"]["x"]
            velY = msgDict["vel"]["y"]
            accumulatorDict["vel"] += math.sqrt(velX ** 2 + velY ** 2)
            velMsgCounter += 1

        if topic == "/common/lap_counter":
            accumulatorDict["laps"] += msgDict["data"]

    # Handle potential zero division (case where no velocity messages were posted)
    if velMsgCounter == 0:
        accumulatorDict["vel"] = 0
    else:
        accumulatorDict["vel"] /= velMsgCounter

    return accumulatorDict

def is_rosbag(objPath):
    file_name, file_extension = os.path.splitext(objPath)

    if not os.path.isfile(objPath):
        return False
    if file_extension != '.bag' and file_extension != '.active':
        return False

    return True

def analyse_dir_content(dirPath, isRecursive=False):
    # Remove existing rosbag_analysis.csv file in this directory (could be outdated)
    analysisFilePath = f'{dirPath}/rosbag_analysis.csv'
    if os.path.isfile(analysisFilePath):
        os.remove(analysisFilePath)
        print(colored(f'[INFO]: Removing {analysisFilePath} - a new analysis file will be created for the directory.', 'cyan'))

    # Add header to the CSV file
    with open(analysisFilePath, 'w', encoding='UTF-8') as f:
        writer = csv.writer(f)
        header = ['file_name', 'per', 'est', 'con', 'vel', 'laps', 'dur']
        writer.writerow(header)

    # Run analysis for this directory
    for objName in os.listdir(dirPath):
        objPath = f'{dirPath}/{objName}'
        # If objName is a ROSBag - analyse it
        if is_rosbag(objPath):
            with open(analysisFilePath, 'a', encoding='UTF-8') as f:
                appender = csv.writer(f)
                # Add row corresponding to current file to CSV
                try:
                    moduleFreq = check_module_freq(objPath)
                    rosbagProperties = check_rosbag_properties(objPath)
                    row = [objPath, int(moduleFreq["per"]), int(moduleFreq["est"]), int(moduleFreq["con"]), rosbagProperties["vel"], rosbagProperties["laps"], moduleFreq["dur"]]
                    appender.writerow(row)

                    # Inform the user via standard output that file was succesfully analysed
                    print(colored(f'[SUCCESS]: File {objPath} has been succesfully analysed.', 'green'))
                # If any exception/error occured - catch it here!
                except rosbag.ROSBagException as err:
                    print(colored(f'[ERROR]: In file {objPath} - {err}', 'red'))
                except KeyboardInterrupt:
                    print("Exiting ...")
        # If objName is a directory and -r flag was passed - analyse the contents of that directory
        elif os.path.isdir(objPath) and isRecursive:
            analyse_dir_content(objPath, isRecursive)
        # If objName is a directory and -r flag was not passed - ignore it
        elif os.path.isdir(objPath) and not isRecursive:
            print(colored(f'[INFO]: Ignoring {objPath} - it is a directory.', 'cyan'))
        # If objName is rosbag_analysis.csv - ignore it
        elif os.path.basename(objPath) == 'rosbag_analysis.csv':
            continue
        # If objName is something else - skip it
        else:
            print(colored(f'[INFO]: Ignoring {objPath} - it is not a ROSBag!', 'cyan'))

def main(args):
    # Check the path which user gave as input
    assert not args.d == "", f'[ERROR]: The script requires the path of the directory to analyse as parameter!'
    assert os.path.isdir(args.d), f'[ERROR]: The passed directory does not exist or cannot be searched!'

    analyse_dir_content(args.d, args.r)
    print(colored(f'[SUCCESS]: Execution finished! All files have been checked out.', 'green'))

if __name__ == "__main__":
    args = analyzer_arg_parser()
    main(args)