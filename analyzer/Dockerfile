FROM ubuntu:20.04
RUN apt update && apt install -y python3-termcolor && apt install -y python3-rosbag && apt install -y python3-pip
RUN pip install --upgrade pip && pip install rospy-message-converter
COPY ./analyzer.py /analyzer.py
ENTRYPOINT ["python3", "analyzer.py"]