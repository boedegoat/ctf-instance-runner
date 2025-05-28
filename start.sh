#!/bin/bash

# Make chall scripts executable
chmod +x chall/start.sh chall/stop.sh

# Start the runner
docker-compose up -d