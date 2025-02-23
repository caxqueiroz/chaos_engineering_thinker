FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/
COPY tests/ tests/
COPY setup.py .

# Create necessary directories with appropriate permissions
RUN mkdir -p /app/data/uploads /app/data/llamaindex \
    && chmod -R 777 /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Use non-root user for security
RUN useradd -m -u 1001 appuser \
    && chown -R appuser:appuser /app
USER 1001

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
