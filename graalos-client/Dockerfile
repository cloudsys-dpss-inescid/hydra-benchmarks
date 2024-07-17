# Use a base image recente do Ubuntu
FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    software-properties-common

RUN apt-get install -y curl
RUN apt-get install -y tmux
RUN apt-get install -y vim
RUN apt-get install -y jq

WORKDIR /scripts

#CMD ["./run-graalhost.sh"]