# Multi-stage build for production
FROM python:3.13.3 AS builder

# Set PATH to include local bin
ENV PATH=/root/.local/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt \
    && pip install --no-cache-dir --user -r requirements-dev.txt

# Production stage
FROM python:3.13.3

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r choibenassist && useradd -r -g choibenassist choibenassist

# Set work directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/choibenassist/.local

# Copy application code
COPY . .

# Change ownership
RUN chown -R choibenassist:choibenassist /app

# Switch to non-root user
USER choibenassist

# Add local bin to PATH
ENV PATH=/home/choibenassist/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
