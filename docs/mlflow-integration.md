# MLflow Integration Guide

This guide explains how to use MLflow for tracing and evaluating your DSPy agent in the FundSearch application.

## Overview

MLflow provides:

- **Tracing**: Automatic logging of all agent interactions, tool calls, and LLM requests
- **Evaluation**: Track performance metrics across different runs
- **Visualization**: Interactive UI to explore agent behavior and debug issues

## Setup

### 1. Install Dependencies

MLflow is already included in the project dependencies. Install it with:

```bash
uv sync
```

### 2. Start MLflow Server

MLflow requires a tracking server to store traces. Start it with:

```bash
# Using SQLite backend (recommended for local development)
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000
```

The server will be available at `http://127.0.0.1:5000`

**Note**: It's highly recommended to use a SQL store (SQLite or PostgreSQL) when using MLflow tracing, as it provides better performance and reliability than the default file store.

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and update the MLflow settings:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# MLflow Configuration
MLFLOW_ENABLED=true
MLFLOW_TRACKING_URI=http://127.0.0.1:5000
MLFLOW_EXPERIMENT_NAME=FundSearch-DSPy
```

## Usage

### Basic Usage with MLflow

```python
import os
from dotenv import load_dotenv
from src.agent.orchestrator import FundSearchOrchestrator

# Load environment variables
load_dotenv()

# Initialize orchestrator with MLflow enabled
orchestrator = FundSearchOrchestrator(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4.1-mini",
    enable_mlflow=True,
    mlflow_tracking_uri=os.getenv("MLFLOW_TRACKING_URI"),
    mlflow_experiment_name=os.getenv("MLFLOW_EXPERIMENT_NAME"),
)

# Use the agent - traces will be automatically logged
answer = orchestrator.ask("Find sustainable energy funds with high ESG ratings")
print(answer)
```

### Programmatic Configuration

You can also configure MLflow directly in code:

```python
from src.agent.orchestrator import FundSearchOrchestrator

orchestrator = FundSearchOrchestrator(
    api_key="your-api-key",
    enable_mlflow=True,
    mlflow_tracking_uri="http://127.0.0.1:5000",
    mlflow_experiment_name="FundSearch-DSPy",
)
```

## Viewing Traces in MLflow UI

### 1. Access the UI

Open your browser and navigate to:

```
http://127.0.0.1:5000
```

### 2. Select Your Experiment

- Click on "Experiments" in the left sidebar
- Select your experiment (e.g., "FundSearch-DSPy")

### 3. View Traces

- Click on the "Traces" tab
- You'll see a list of all agent executions with timestamps

### 4. Inspect Individual Traces

Click on any trace to see:

- **Input/Output**: The question asked and the answer generated
- **Tool Calls**: All tool invocations (parse_query, search_db)
- **LLM Calls**: Model inputs, outputs, and configurations
- **Execution Time**: How long each step took
- **Token Usage**: Tokens consumed by each LLM call

## What Gets Traced

MLflow automatically captures:

1. **Agent Predictions**

   - Input questions
   - Final answers
   - Full execution trajectory

2. **Tool Invocations**

   - Tool name
   - Input parameters
   - Output results

3. **LLM Calls**

   - Model name and configuration
   - Prompt sent to the model
   - Model response
   - Token usage
   - Latency

4. **Metadata**
   - Timestamp
   - Experiment name
   - Run ID

## Debugging with MLflow

### Example: Debugging Poor Results

If your agent gives incorrect answers:

1. Open the trace in MLflow UI
2. Inspect the tool outputs:
   - Did the query parser extract the right parameters?
   - Did the search return relevant results?
3. Check LLM inputs:
   - Is the context provided to the model sufficient?
   - Are the tool results formatted correctly?
4. Review the reasoning chain:
   - How many iterations did the agent take?
   - What was the thought process at each step?

### Example Trace Navigation

```
Trace View
├── Input: "Find sustainable energy funds"
├── Step 1: parse_query
│   ├── Input: {"query": "sustainable energy funds"}
│   └── Output: {"investment_type": "fund", "sustainability": true, ...}
├── Step 2: search_db
│   ├── Input: {"investment_type": "fund", "sustainability": true}
│   └── Output: [{"name": "Green Energy Fund", ...}, ...]
├── Step 3: LLM Final Response
│   ├── Context: [tool results]
│   └── Output: "Here are the sustainable energy funds..."
└── Final Answer: "Here are the sustainable energy funds..."
```

## Advanced Features

### Multiple Experiments

Organize traces by use case:

```python
# Development experiment
dev_orchestrator = FundSearchOrchestrator(
    api_key=api_key,
    enable_mlflow=True,
    mlflow_experiment_name="FundSearch-Dev",
)

# Production experiment
prod_orchestrator = FundSearchOrchestrator(
    api_key=api_key,
    enable_mlflow=True,
    mlflow_experiment_name="FundSearch-Prod",
)
```

### Evaluation Metrics

MLflow can track custom metrics across runs. You can extend the orchestrator to log:

- Accuracy
- Response time
- User satisfaction scores
- Tool usage patterns

## Troubleshooting

### MLflow Server Not Running

**Error**: `ConnectionError: Cannot connect to MLflow tracking server`

**Solution**: Ensure the MLflow server is running:

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000
```

### Traces Not Appearing

**Checklist**:

1. Is `enable_mlflow=True` in the orchestrator initialization?
2. Is the MLflow tracking URI correct?
3. Is the MLflow server running and accessible?
4. Check the server logs for errors

### Wrong Experiment

If traces appear in the wrong experiment:

1. Check the `mlflow_experiment_name` parameter
2. MLflow creates new experiments automatically if they don't exist

## Best Practices

1. **Use SQL Backend**: Always use SQLite or PostgreSQL for the MLflow backend when using tracing
2. **Separate Experiments**: Use different experiments for dev, staging, and production
3. **Regular Review**: Periodically review traces to identify common failure patterns
4. **Clean Up**: Archive old experiments to keep the UI performant
5. **Secure Access**: In production, add authentication to your MLflow server

## Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [DSPy + MLflow Tutorial](https://dspy.ai/tutorials/observability/#tracing)
- [MLflow Tracing Guide](https://mlflow.org/docs/latest/llms/tracing/index.html)
