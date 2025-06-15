#!/usr/bin/env bash
# start.sh

# 1) Start the Rasa action server in the background
rasa run actions --actions actions &
ACTION_PID=$!

# 2) Start the Rasa core server (with REST API)
rasa run --enable-api --cors "*" --host 0.0.0.0 --port $PORT
