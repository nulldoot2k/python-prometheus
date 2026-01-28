FROM python:3.11-slim

# Create non-root user
RUN useradd -m myuser -u 1000

WORKDIR /app

# Copy application files
COPY app.py .
COPY requirements.txt .
COPY templates/ templates/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Change ownership
RUN chown -R myuser:myuser /app

# Switch to non-root user
USER myuser

# Expose ports
EXPOSE 8080 9090

# Run application
CMD ["python", "app.py"]
