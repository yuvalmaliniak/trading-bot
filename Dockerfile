# Use the official Python image as a base
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first (for caching dependencies)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose a port if the app has a web API (optional, update if needed)
EXPOSE 8000

# Define the entrypoint to run the app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

