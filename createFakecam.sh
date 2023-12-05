#!/bin/bash
# create a network

docker build -t bodypix ./bodypix   

docker build -t fakecam ./fakecam

sudo modprobe -r v4l2loopback
sudo modprobe v4l2loopback devices=1 video_nr=20 card_label="v4l2loopback" exclusive_caps=1

docker network create --driver bridge fakecam
sleep 7
echo "Are you installing this with a nvidia-gpu installed? 1=y 2=n"

read install_type

if [ $install_type -eq 1 ];
then
# start the bodypix app
docker create \
  --name=bodypix \
  --network=fakecam \
  -p 9000:9000 \
  --gpus=all --device /dev/nvidia0 --device /dev/nvidia-uvm --device /dev/nvidia-uvm-tools --device /dev/nvidiactl \
  --shm-size=1g --ulimit memlock=-1 --ulimit stack=67108864 \
  bodypix

else
docker create \
  --name=bodypix \
  --network=fakecam \
  -p 9000:9000 \
  bodypix
fi

sleep 10
# start the camera, note that we need to pass through video devices,
# and we want our user ID and group to have permission to them
# you may need to `sudo usermod -aG video $USER`
docker create \
  --name=fakecam \
  --network=fakecam \
  -u 1000:986 \
  --device /dev/video2 \
  --device /dev/video20 \
  fakecam