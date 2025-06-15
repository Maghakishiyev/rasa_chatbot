#!/usr/bin/env bash
# start.sh

# 1. start the Rasa HTTP server on the Render‐provided $PORT
rasa run \
  --enable-api \
  --cors '*' \
  --host 0.0.0.0 \
  --port "$PORT" &

# 2. start the action server on port 5055
rasa run actions \
  --actions actions \
  --port 5055
