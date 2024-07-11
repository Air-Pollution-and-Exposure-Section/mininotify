# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git && apt-get clean

# Copy the entire project directory into the container
COPY . .

# Install the project in editable mode
RUN pip install -e .

# Define the command to run your script
CMD ["python", "runners/daily-report/main.py"]

