import argparse
import os
import pandas as pd # Use to read the rosbag_analysis.csv file
from termcolor import colored

# Use to show full columns of pandas DataFrame (remove cutoff)
pd.set_option('display.max_colwidth', None)

def filter_arg_parser():
    # Create a parser object to handle commandline input
    parser = argparse.ArgumentParser(description="ROSBag Filter", epilog="If you have propositions for other flags,\nfeel free to create an issue on GitHub!\nMaintainer: S.Piasecki")

    # Add the different parser arguments
    parser.add_argument('--per', action='store_true', help="Filter for rosbags where perception runs at ~10 Hz")
    parser.add_argument('--est', action='store_true', help="Filter for rosbags where estimation runs at ~10 Hz")
    parser.add_argument('--con', action='store_true', help="Filter for rosgags where control runs at ~10 Hz")

    parser.add_argument('--vel', type=int, default=1, help="Filter for rosbags where avg. car velocity (in m/s) is at least VEL (default: 1)")
    parser.add_argument('--laps', type=int, default=0, help="Filter for rosbags where car does at least LAPS laps (default: 0)")
    parser.add_argument('--dur', type=int, default=60, help="Filter for rosbags which are at least DUR seconds long (default: 60)")

    parser.add_argument('-d', type=str, help="Not optional - take an absolute path to a directory and analyses all ROSBags within it", required=True)
    parser.add_argument('-r', action='store_true', help="The directory with rosbags is filtered recursively (entire file tree starting at given path is filtered).")

    args = parser.parse_args()
    return args

def filter_dir_content(dirPath, args, isRecursive=False):
    analysisFileName = f'{dirPath}/rosbag_analysis.csv'
    if not os.path.isfile(analysisFileName):
        runAnalyser = input(colored(f'[ERROR]: The file rosbag_analysis.csv has not been found in the directory /home/amz-nas{dirPath}. Please run analyzer on this directory first.', 'red'))
        print(colored(f'[ERROR]: Cannot procede with filtering. Closing the program ...', 'red'))
        exit()

    # If user wants to filter recursively - filter again in each nested directory
    if isRecursive:
        for objName in os.listdir(dirPath):
            objPath = f'{dirPath}/{objName}'
            if os.path.isdir(objPath):
                filter_dir_content(objPath, args, isRecursive)

    # File rosbag_analysis.csv exists and has been found, hence proceed with the filtering
    df = pd.read_csv(analysisFileName)
    # Filter the pandas DataFrame for ROSBags which meet the criteria given by the user
    df = df.loc[(df["per"] >= args.per) & (df["est"] >= args.est) & (df["con"] >= args.con) & (df["vel"] >= args.vel) & (df["laps"] >= args.laps) & (df["dur"] >= args.dur)]
    # Print the paths of the filtered ROSBags
    print(df['file_name'].to_string(index=False))

def main(args):
    assert not args.d == "", f'[ERROR]: The script requires the path of the directory to analyse as parameter!'
    assert os.path.isdir(args.d), f'[ERROR]: The passed directory does not exist or cannot be searched!'

    filter_dir_content(args.d, args, args.r)

    print(colored('Filtering completed!', 'cyan'))

if __name__ == "__main__":
    args = filter_arg_parser()
    main(args)