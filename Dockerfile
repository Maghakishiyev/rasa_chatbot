# 1. Base image with Rasa installed
FROM rasa/rasa:3.6.21-full

USER root

# 2. Set working dir
WORKDIR /app

# 3. Copy your project files into the container
COPY . /app

# 4. Install custom action dependencies
RUN pip install --no-cache-dir rasa-sdk requests

# 5. Expose Rasa REST API (5005) and action server (5055)
EXPOSE 5005
EXPOSE 5055

# 6. Switch to non-root (best practice)
USER 1001

# 7. Shell-form CMD so $PORT expands, starting both servers:
#    - Rasa core on $PORT (Render sets $PORT automatically)
#    - Rasa action server on 5055
CMD bash -lc "\
  rasa run --enable-api --cors '*' --host 0.0.0.0 --port \$PORT & \
  rasa run actions --actions actions --port 5055 \
"
