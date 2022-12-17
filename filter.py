import argparse

def arg_parser():
    # Create a parser object to handle commandline input
    parser = argparse.ArgumentParser(description="Rosbag Filter", epilog="If you have propositions for other flags,\nfeel free to create an issue on GitHub!\nMaintainer: S.Piasecki")

    # Add the different parser arguments
    parser.add_argument('--per', action='store_true', help="Filter for rosbags where perception runs at ~10 Hz")
    parser.add_argument('--est', action='store_true', help="Filter for rosbags where estimation runs at ~10 Hz")
    parser.add_argument('--con', action='store_true', help="Filter for rosgags where control runs at ~10 Hz")

    parser.add_argument('-v', action='store_true', default=True, help="Filter for rosbags where the car moves")
    parser.add_argument('-c', default=0, help="Filter for rosbags where car does at least X laps")
    parser.add_argument('-l', default=60, help="Filter for rosbags which are at least x seconds long")

    parser.add_argument('-d', type=str, help="Takes an absolute path to a directory and loads all rosbags within it be analysed")
    parser.add_argument('-r', type=str, help="The directory with rosbags is filtered recursively (entire file tree starting at given path is analysed). WARNING - can be very slow!")
    parser.add_argument('-s', type=str, help="Takes an absolute path to a directory where the filtered rosbags should be stored")

    parser.add_argument('--nas-load', action='store_true', help="Load directory from the NAS")
    parser.add_argument('--nas-upload', action='store_true', help="Upload filtered rosbags to the NAS")

    args = parser.parse_args()
    return args