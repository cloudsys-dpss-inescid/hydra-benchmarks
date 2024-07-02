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

#Get acess to the GPU https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html and https://github.com/NVIDIA/nvidia-container-toolkit?tab=readme-ov-file
#the host machine needs to have the Nvidia drivers instaled
RUN curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
&& curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
RUN sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list  
RUN apt-get update
RUN apt-get install -y nvidia-container-toolkit
RUN nvidia-ctk runtime configure --runtime=docker
#RUN systemctl restart docker

CMD ["python3", "/data-forecast/http_server.py"]
