# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire mininotify directory into the container
COPY . /app/mininotify

# Change directory to skynet and install the package in editable mode
RUN cd mininotify/skynet && pip install -e .

# Set the working directory to mininotify
WORKDIR /app/mininotify

# Run the command to execute your application
CMD ["python3", "main.py"]

