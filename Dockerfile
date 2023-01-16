FROM ros:noetic
RUN apt update && apt install -y python3-pandas && apt install -y python3-termcolor && apt install -y python3-rosbag
RUN apt install -y python3-pip && pip install rospy-message-converter