# AMZ ROSBag Filter v2.2

## What is it?

This tool allows for simple and efficient search for potentially useful _ROSBags_. The idea is: whenever you are looking for a specific _ROSBag_, you can tell the tool what you need and it will output **paths** to _ROSBags_ which **could** be potentially interesting for you. This spares you the effort of investigating every single _ROSBag_ manually with `rosbag info` or trying all of them out with the simulator.

## Installation

The tool is targeted to use on the **NAS**, where it has already been installed and is **ready to use** (have a look at `Usage` section of this README), but you could theoretically also deploy it on your local machine. For this you need to:

1. Make sure you have Docker installed
2. Clone the `v2.2` tag of the repository - `git clone -b v2.2 https://github.com/AMZ-Driverless/amz-rosbag-filter.git`
3. Adapt the paths of the mounts in the `docker-compose.yml`. You need to mount each directory that you would like to analyze/filter to a directory in the Docker container. For example: in the NAS `docker-compose.yml`, the directory `/home/amz-nas/castor-2023` is mounted to the `/castor-2023` directory in the file system of the container. In order to analyze/filter that directory you have to pass the **container** path as argument to the script
4. Run `docker-compose build` in the root of directory
5. Make sure the build was successful by running `docker images` and making sure `amz-rosbag-analyzer` and `amz-rosbag-filter` are both listed

## Usage

This version consists of **two** Python scripts:

1. `analyzer.py` - used for generating CSV files which contain the properties of different _ROSBags_
2. `filter.py` - takes as input the parameters desired by the user and searches through the CSV files generated by the analyzer to find _ROSBags_, which satisfy the demanded properties

In order to use them on the NAS, you have to SSH to the NAS server and execute following commands **in the root of the repository** (`/home/amz-nas/amz-rosbag-filter`):

`amz-rosbag-analyzer [additional arguments]` - to run the **analyzer**

`amz-rosbag-filter [additional arguments]` - to run the **filter**

Keep in mind that both `amz-rosbag-analyzer` and `amz-rosbag-filter` are **bash aliases!** If you want to use the tool locally on your machine **OR** the above aliases do not work on the NAS use:

`docker-compose run --rm amz-rosbag-analyzer [additional arguments]` - to run the **analyzer**

`docker-compose run --rm amz-rosbag-filter [additional arguments]` - to run the **filter**

You have to pass additional **flags/arguments** to all the commands above to acquire the desired behaviour.
For `analyzer.py` these include:

```bash
  -h, --help  show this help message and exit
  -d D        Not optional (!) - take an absolute path to a directory and analyses all ROSBags within it
  -r          The directory passed with -d flag is searched recursively (entire file tree starting at given path is
              analysed). WARNING - can be very slow!
```

And for `filter.py`:

```bash
  -h, --help   show this help message and exit
  -d D         Not optional (!) - take a relative path to a directory and analyses all ROSBags within it
  -r           The directory with ROSBags is filtered recursively (entire file tree starting at given path is filtered)
  --per        Filter for ROSBags where perception runs at ~10 Hz
  --est        Filter for ROSBags where estimation runs at ~10 Hz
  --con        Filter for ROSBags where control runs at ~10 Hz
  --vel VEL    Filter for ROSBags where avg. car velocity (in m/s) is at least VEL (default: 1)
  --laps LAPS  Filter for ROSBags where car does at least LAPS laps (default: 0)
  --dur DUR    Filter for ROSBags which are at least DUR seconds long (default: 60)
  --ve         Filter for ROSBags with VE data
  --imu        Filter for ROSBags with IMU data
  --ass        Filter for ROSBags with ASS data
  --ins        Filter for ROSBags with INS data
```

**Examples**:

```bash
# Analyse the directory /home/amz-nas/pilatus-2022/2022-07-29_IPZ/rosbags-small to create the rosbag_analysis.csv file used by filter
docker-compose run --rm amz-rosbag-analyzer -d /pilatus-2022/2022-07-29_IPZ/rosbags-small

# Analyse the directory /home/amz-nas/pilatus-2022/2022-07-29_IPZ recursively and create rosbag_analysis.csv in each encountered directory
docker-compose run --rm amz-rosbag-analyzer -d /pilatus-2022/2022-07-29_IPZ -r

# Recursively filter the directory /home/amz-nas/bernina-2022/2022-08-03_IPZ for ROSBags where perception and control run at ~10 Hz, avg. velocity is equal to at least 2m/s and the duration is at least 90 seconds.
docker-compose run --rm amz-rosbag-filter -d /bernina-2022/2022-08-03_IPZ -r --per --con --vel 2 --dur 90

# Filter the directory /home/amz-nas/pilatus-2022/2022-06-08_IPZ/rosbags for ROSBags where estimation runs at ~10 Hz and the car does at least 2 laps.
docker-compose run --rm amz-rosbag-filter -d /pilatus-2022/2022-06-08_IPZ/rosbags --con --laps 2

# Filter the directory /home/amz-nas/pilatus-2022/2022-06-08_IPZ/rosbags recursively for ROSBags where estimation runs at ~10 Hz and VE and INS data is present
docker-compose run --rm amz-rosbag-filter -d /pilatus-2022/2022-06-08_IPZ/rosbags -r --est --ve --ins
```

**Important:** do not forget the `--rm` flag when using the `docker-compose` command! Also - only directories mounted in the `docker-compose.yml` can be analyzed/filtered!

## Additional functionality

If there are any properties that you would like to filter the _ROSBags_ after, that you (and maybe also the rest of the team) could make use of, please create an issue in this repository! I am open for any suggestions!

Maintainer: Stanislaw Piasecki
