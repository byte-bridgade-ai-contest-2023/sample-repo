#!/bin/bash

docker container rm fakecam
docker container rm bodypix
docker image rm fakecam
docker image rm bodypix
docker network rm fakecam