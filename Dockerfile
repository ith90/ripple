# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Update the package list and install git
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
&& rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy the entire application
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
