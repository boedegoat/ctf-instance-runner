#!/bin/bash

# $1 = port
# $2 = instance name
docker_compose_path="$(pwd)/chall/docker-compose.yml"
PORT=$1 docker-compose -f "${docker_compose_path}" -p $2 up --build -d
