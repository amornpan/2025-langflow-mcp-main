# Multi-stage build for smaller final image
FROM python:3.11-slim as builder
# Install build dependencies
RUN apt-get update && apt-get install -y \
 gcc \
 g++ \
 && rm -rf /var/lib/apt/lists/*
# Set working directory
WORKDIR /app
# Copy requirements first for better caching
COPY requirements.txt .
# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt
# Final stage
FROM python:3.11-slim
# Install runtime dependencies including telnet, wget, curl
RUN apt-get update && apt-get install -y \
 libgomp1 \
 telnet \
 wget \
 curl \
 && rm -rf /var/lib/apt/lists/*
# Create non-root user
RUN useradd -m -u 1000 mcpuser
# Create documents directory
RUN mkdir -p /home/mcpuser/documents && chown mcpuser:mcpuser /home/mcpuser/documents
# Set working directory
WORKDIR /app
# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/mcpuser/.local
# Copy application code
COPY --chown=mcpuser:mcpuser . .
# Copy all markdown files to documents directory
COPY --chown=mcpuser:mcpuser *.md /home/mcpuser/documents/
# Switch to non-root user
USER mcpuser
# Add local bin to PATH
ENV PATH=/home/mcpuser/.local/bin:$PATH
# Expose port
EXPOSE 8000
# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"
# Run the application
CMD ["python", "main.py"]