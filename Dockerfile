FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    libmariadb-dev-compat \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create transcriptions directory
# RUN mkdir -p transcriptions

# Expose port

# Set environment variables
# ENV FLASK_APP=app.py
# ENV FLASK_ENV=production

# Run the application
# CMD ["python", "run.py"]
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:6001", "run:app"]

EXPOSE 6001