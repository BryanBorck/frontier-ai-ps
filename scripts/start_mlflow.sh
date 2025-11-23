#!/bin/bash
# Start MLflow tracking server with SQLite backend

# Default values
PORT="${MLFLOW_PORT:-5001}"
DB_PATH="src/mlflow/mlflow.db"
ARTIFACTS_PATH="./src/mlflow/mlartifacts"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting MLflow tracking server...${NC}"
echo -e "${BLUE}Port: ${PORT}${NC}"
echo -e "${BLUE}Database: ${DB_PATH}${NC}"
echo -e "${BLUE}Artifacts: ${ARTIFACTS_PATH}${NC}"
echo ""

# Create directories if they don't exist
mkdir -p "$(dirname "$DB_PATH")"
mkdir -p "$ARTIFACTS_PATH"

# Start the server using uv to access the mlflow command
uv run mlflow server \
    --backend-store-uri "sqlite:///${DB_PATH}" \
    --default-artifact-root "${ARTIFACTS_PATH}" \
    --port "${PORT}" \
    --host 127.0.0.1

echo -e "${GREEN}MLflow server stopped.${NC}"
