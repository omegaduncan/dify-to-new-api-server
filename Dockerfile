# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir flask requests python-dotenv

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Use ARG to pass build-time variables
ARG DIFY_URL
ARG DIFY_KEY

# Set environment variables
ENV DIFY_URL=$DIFY_URL
ENV DIFY_KEY=$DIFY_KEY

# Run server.py when the container launches
CMD ["python", "server.py"]
