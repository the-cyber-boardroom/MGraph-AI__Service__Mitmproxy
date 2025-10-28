#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .local-server.env ]; then
    echo "Loading environment variables from .local-server.env file..."
    export $(cat .local-server.env | grep -v '^#' | grep -v '^[[:space:]]*$' | xargs)
    echo "✓ Environment variables loaded"
else
    echo "⚠️  Warning: .env file not found"
    echo "   Create a .env file with your configuration"
fi

uvicorn mgraph_ai_service_mitmproxy.fast_api.lambda_handler:app --reload --host 0.0.0.0 --port 10016 \
    --log-level info \
    --no-access-log