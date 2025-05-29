# Use an official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port (change this if your FastAPI app runs on a different port)
EXPOSE 8000

# Command to run the app (adjust for your entry point)
CMD ["uvicorn", "voice_api:app", "--host", "0.0.0.0", "--port", "8000"]
