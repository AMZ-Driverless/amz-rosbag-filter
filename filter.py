import argparse
import os
import pandas as pd # Use to read the rosbag_analysis.csv file
from termcolor import colored

def filter_arg_parser():
    # Create a parser object to handle commandline input
    parser = argparse.ArgumentParser(description="ROSBag Filter", epilog="If you have propositions for other flags,\nfeel free to create an issue on GitHub!\nMaintainer: S.Piasecki")

    # Add the different parser arguments
    parser.add_argument('--per', action='store_true', help="Filter for rosbags where perception runs at ~10 Hz")
    parser.add_argument('--est', action='store_true', help="Filter for rosbags where estimation runs at ~10 Hz")
    parser.add_argument('--con', action='store_true', help="Filter for rosgags where control runs at ~10 Hz")

    parser.add_argument('--vel', type=int, default=1, help="Filter for rosbags where avg. car velocity is at least X")
    parser.add_argument('--laps', type=int, default=0, help="Filter for rosbags where car does at least X laps")
    parser.add_argument('--dur', type=int, default=60, help="Filter for rosbags which are at least X seconds long")

    parser.add_argument('-d', type=str, help="Takes an absolute path to a directory and loads all rosbags within it be filtered")
    parser.add_argument('-r', action='store_true', help="The directory with rosbags is filtered recursively (entire file tree starting at given path is filtered).")

    args = parser.parse_args()
    return args

# TODO: Add recursive execution for nested directories
def main(args):
    assert not args.d == "", f'[ERROR]: The script requires the path of the directory to analyse as parameter!'
    assert os.path.isdir(args.d), f'[ERROR]: The passed directory does not exist!'

    analysisFileName = f'{args.d}/rosbag_analysis.csv'
    if not os.path.isfile(analysisFileName):
        runAnalyser = input(colored(f'[INFO]: The file rosbag_analysis.csv has not been found in the given directory. Would you like to run analyzer first? [y/N]', 'cyan'))
        if runAnalyser == 'y':
            # TODO: Run analyser if the user decides to do so
            print(colored("[INFO]: Running analyser ...", "cyan"))
        else:
            print(colored(f'[ERROR]: Cannot procede with filtering. Closing the program ...', 'red'))
            exit()

    # File rosbag_analysis.csv exists and has been found, hence proceed with the filtering
    df = pd.read_csv(analysisFileName)
    # Filter the pandas DataFrame for ROSBags which meet the criteria given by the user
    df = df.loc[(df["per"] >= args.per) & (df["est"] >= args.est) & (df["con"] >= args.con) & (df["vel"] >= args.vel) & (df["laps"] >= args.laps) & (df["dur"] >= args.dur)]
    # Print the paths of the filtered ROSBags
    print(colored('The ROSBags which fulfill the given criteria are: ', 'cyan'))
    print(df['file_name'])


if __name__ == "__main__":
    args = filter_arg_parser()
    main(args)