# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY app.py .

# Expose port 80 (where Flask app listens)
EXPOSE 80

# Define environment variable for Flask
ENV FLASK_APP=app.py

# Run the application
# Use 'python -m flask run' for development, or 'gunicorn' for production
# For simplicity in this lab, we'll use Flask's built-in server.
CMD ["python", "app.py"]