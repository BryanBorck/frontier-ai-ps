# Helper Scripts

This directory contains helper scripts for running and managing the project.

## MLflow Server

### Starting the MLflow Server

To start the MLflow tracking server with the correct configuration:

```bash
./scripts/start_mlflow.sh
```

The server will:
- Run on port 5001 (configurable via `MLFLOW_PORT` environment variable)
- Store data in `src/mlflow/mlflow.db` (SQLite)
- Store artifacts in `src/mlflow/mlartifacts`
- Be accessible at `http://127.0.0.1:5001`

### Custom Port

To use a different port:

```bash
MLFLOW_PORT=5002 ./scripts/start_mlflow.sh
```

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Running the Agent with MLflow

Once the MLflow server is running, you can use the CLI with MLflow tracing enabled:

```bash
# Ask a single question with MLflow tracing
uv run dspy-agent ask "Find funds managed by BTG Pactual" --mlflow

# Start an interactive chat with MLflow tracing
uv run dspy-agent chat --mlflow
```

The traces will be automatically logged to the MLflow server and can be viewed in the UI at `http://127.0.0.1:5001`.
