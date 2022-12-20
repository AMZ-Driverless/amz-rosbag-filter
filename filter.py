import argparse
import pandas # Use to read the rosbag_analysis.csv file

def arg_parser():
    # Create a parser object to handle commandline input
    parser = argparse.ArgumentParser(description="Rosbag Filter", epilog="If you have propositions for other flags,\nfeel free to create an issue on GitHub!\nMaintainer: S.Piasecki")

    # Add the different parser arguments
    parser.add_argument('--per', action='store_true', help="Filter for rosbags where perception runs at ~10 Hz")
    parser.add_argument('--est', action='store_true', help="Filter for rosbags where estimation runs at ~10 Hz")
    parser.add_argument('--con', action='store_true', help="Filter for rosgags where control runs at ~10 Hz")

    parser.add_argument('--vel', default=1, help="Filter for rosbags where avg. car velocity is at least X")
    parser.add_argument('--laps', default=0, help="Filter for rosbags where car does at least X laps")
    parser.add_argument('--dur', default=60, help="Filter for rosbags which are at least X seconds long")

    parser.add_argument('-d', type=str, help="Takes an absolute path to a directory and loads all rosbags within it be analysed")
    parser.add_argument('-r', type=str, help="The directory with rosbags is filtered recursively (entire file tree starting at given path is analysed). WARNING - can be very slow!")
    parser.add_argument('-s', type=str, help="Takes an absolute path to a directory where the filtered rosbags should be stored")

    args = parser.parse_args()
    return args