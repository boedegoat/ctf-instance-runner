#!/bin/bash

docker_compose_path="$(pwd)/chall/docker-compose.yml"
PORT=$1 docker-compose -f "${docker_compose_path}" -p $2 down
