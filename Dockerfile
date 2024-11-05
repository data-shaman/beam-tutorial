# Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Generate synthetic data
RUN python scripts/generate_data.py

# Set the entry point
ENTRYPOINT ["python", "main.py"]