# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Expose port 8000 to allow external access
EXPOSE 8000
