FROM python:3.11-slim

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -o /usr/local/bin/ollama https://ollama.com/downloads/ollama-linux \
    && chmod +x /usr/local/bin/ollama

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

# Expose FastAPI and Ollama ports
EXPOSE 8000 11434

# Start both Ollama and FastAPI servers using a process manager
CMD ["sh", "-c", "ollama serve & uvicorn main:app --host 0.0.0.0 --port 8000"]