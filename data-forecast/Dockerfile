# Use a base image recente do Ubuntu
FROM ubuntu:latest

# I get the corret python version from here:https://gist.github.com/rutcreate/c0041e842f858ceb455b748809763ddb . Autogluon needs a specific Python version.
RUN apt-get update && apt-get install -y \
    software-properties-common


RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    curl

RUN ls -la /usr/bin/python3
RUN rm /usr/bin/python3
RUN ln -s python3.10 /usr/bin/python3
RUN python3 --version

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
RUN python3 -m pip --version


RUN apt-get update
RUN apt-get install -y libtbb-dev
RUN pip3 install tbb
RUN pip3 install numba

RUN pip3 install autogluon
RUN pip3 install stumpy


CMD ["python3", "/data-forecast/http_server.py"]
