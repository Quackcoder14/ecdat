FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    nodejs \
    npm \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install scanning tools
# Install TreeSitter CLI
RUN npm install -g tree-sitter-cli

# Install Semgrep
RUN pip install semgrep

# Install Syft for dependency scanning
RUN curl -fsSL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Install essential TreeSitter language parsers
RUN tree-sitter init-config
RUN npm install -g tree-sitter-python tree-sitter-javascript tree-sitter-go tree-sitter-java tree-sitter-c tree-sitter-cpp

# Copy application code
COPY . .

# Add scanner to Python path (will be mounted via docker-compose)
ENV PYTHONPATH="/app:/app/scanner"

# Create artifacts directory
RUN mkdir -p /app/artifacts

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]