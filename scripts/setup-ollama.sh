#!/bin/bash
# Setup Ollama with default model

MODEL=${1:-"llama3.2"}

echo "Setting up Ollama with model: $MODEL"
echo "This may take a few minutes..."

docker-compose exec ollama ollama pull "$MODEL"

echo ""
echo "Ollama setup complete!"
echo "Model '$MODEL' is ready to use."
