FROM rasa/rasa:3.6.21-full

USER root
WORKDIR /app

# Copy code + the start script
COPY . /app

# Install your custom action dependencies
RUN pip install --no-cache-dir rasa-sdk requests

# Expose the two ports (Render will use $PORT==5005 for the web service)
EXPOSE 5005 5055

# Clear the base image ENTRYPOINT (which points at `rasa`)
ENTRYPOINT []

# Switch back to non-root
USER 1001

# Launch both servers via our script
CMD ["bash", "/app/start.sh"]
