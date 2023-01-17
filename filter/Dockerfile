FROM ubuntu:20.04
RUN apt update && apt install -y python3-pandas && apt install -y python3-termcolor
COPY ./filter.py /filter.py
ENTRYPOINT ["python3", "/filter.py"]