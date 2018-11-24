#!/bin/bash

docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
mkdir -p ~/camera_latest
rm -fr ~/camera_latest/*
cd ~/camera_latest && git clone https://github.com/armindocachada/tensorflow-with-object-recognition
cp ~/project/config/config.ini ~/camera_latest/tensorflow-with-object-recognition
cd ~/camera_latest//tensorflow-with-object-recognition
docker build -t armindocachada/tensorflow-with-object-recognition -f Dockerfile_pi .
docker run -i -t -d -p 8888:8888 -v /share:/data/videos/incoming armindocachada/tensorflow-with-object-recognition
