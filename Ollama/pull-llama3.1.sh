#!/bin/bash
# Pull the model and serve Ollama

# Start the Ollama server in the background
./bin/ollama serve &

# Store PID of the server
pid=$!

# Give the server some time to start
sleep 5

# Pull the Llama 3.1 model
echo "Pulling llama3.1 model..."
ollama pull llama3.1

# Wait for the Ollama server to keep running
wait $pid