FROM rasa/rasa:3.6.21-full
USER root

# Copy project files
COPY . /app
WORKDIR /app

# Create requirements.txt with necessary dependencies
RUN echo "rasa==3.6.21" > requirements.txt

# Install any custom action dependencies
RUN pip install -r requirements.txt

# Expose Rasa ports (5005 for the REST channel, 5055 for actions)
EXPOSE 5005 5055

# Switch to non-root user (security best practice)
USER 1001

# Default entry—when container starts, it'll run both server + action server
CMD ["run", "--enable-api", "--cors", "*"]