FROM ollama/ollama:latest

# Copy the script that pulls the model
COPY ./pull-llama3.1.sh /pull-llama3.1.sh

# Set executable permission
RUN chmod +x /pull-llama3.1.sh

# Entry point (runs the script in foreground)
ENTRYPOINT ["/bin/bash", "/pull-llama3.1.sh"]