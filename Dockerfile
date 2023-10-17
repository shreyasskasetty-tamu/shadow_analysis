# Using an official Python base image from the DockerHub
FROM python:3.11-slim

# Sets the working directory for following COPY and CMD instructions
WORKDIR /app

# Copies the requirements.txt file
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copies the content of the local src directory to the working directory
COPY . .

# Specifies the command to run when the image is used as the base for another image
CMD ["gunicorn", "--bind", "0.0.0.0:5001","shadow_analysis.factory:create_app()", "--access-logfile", "-", "--error-logfile", "-"]