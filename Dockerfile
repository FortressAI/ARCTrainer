# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Expose the port for the Flask app
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
