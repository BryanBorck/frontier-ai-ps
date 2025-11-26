# MLflow Integration Guide

This guide explains how to use MLflow for tracing and evaluating your DSPy agent in the FundSearch application.

## Overview

MLflow provides:
- **Tracing**: Automatic logging of all agent interactions, tool calls, and LLM requests.
- **Evaluation**: Track performance metrics across different runs.
- **Visualization**: Interactive UI to explore agent behavior and debug issues.

## Setup

### 1. Start MLflow Server

MLflow requires a tracking server to store traces. We recommend using a persistent backend like SQLite for local development.

```bash
# Start the server using the provided script
./scripts/start_mlflow.sh
```

This starts the server at `http://127.0.0.1:5001` with a SQLite backend located at `src/infrastructure/mlflow/mlflow.db`.

### 2. Configure Environment

Ensure your `.env` file has the following configurations:

```env
# MLflow Configuration
MLFLOW_ENABLED=true
MLFLOW_TRACKING_URI=http://127.0.0.1:5001
MLFLOW_EXPERIMENT_NAME=FundSearch-Agent
```

## Usage

### Using the CLI

The easiest way to use MLflow is via the CLI with the `--mlflow` flag.

```bash
# Chat mode with tracing enabled
uv run dspy-agent chat --mlflow

# Single question with tracing
uv run dspy-agent ask "Find high-yield funds" --mlflow
```

### Programmatic Usage

If you are using the `FundSearchTool` directly in your code:

```python
from src.agent.fund_search.orchestrator import FundSearchTool

# Initialize tool with MLflow enabled
tool = FundSearchTool(
    api_key="...",
    enable_mlflow=True,
    mlflow_tracking_uri="http://127.0.0.1:5001",
    mlflow_experiment_name="FundSearch-Agent"
)

# Traces will be automatically logged
result = tool.ask("Find funds managed by Kinea")
```

## Viewing Traces

1. Open `http://127.0.0.1:5001` in your browser.
2. Select the **FundSearch-Agent** experiment.
3. Click on the **Traces** tab.
4. Click on a trace ID to view the full execution tree:
   - **Root Span**: Total latency and final output.
   - **IntentClassification**: How the agent understood the query.
   - **CriteriaExtraction**: Extracted parameters.
   - **SearchExecution**: Database queries and results.

## Debugging Tips

If the agent returns "No results":
1. Check the **CriteriaExtraction** span. Did it extract the correct filters?
2. Check the **SearchExecution** span. Did the SQL query look correct?
3. Check the **IntentClassification**. Was the query ambiguous?

## Storage Warning

The MLflow database and artifacts can grow large. They are stored in `src/infrastructure/mlflow/` and should generally be ignored by git (added to `.gitignore`).
