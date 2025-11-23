# DSPy Agent CLI

A command-line interface for interacting with DSPy agents with conversation history management. This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management and [DSPy](https://github.com/stanfordnlp/dspy) for building language model programs.

## Features

- **Conversation History**: Maintains context across chat sessions using DSPy's History utility
- **Interactive Chat Mode**: Have natural conversations with the agent
- **Single-Question Mode**: Ask one-off questions without history
- **Rich Terminal UI**: Beautiful interface with tables, panels, and syntax highlighting
- **Flexible Model Support**: Works with OpenAI and other LiteLLM-supported models
- **History Commands**: View and manage conversation history in real-time
- **Environment-based Configuration**: Easy setup with .env files
- **MLflow Integration**: Optional tracing and evaluation of agent interactions

## Prerequisites

- Python 3.13+
- uv package manager
- API key for Gemini (default) or OpenAI

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd frontier-ai-ps
```

2. Install dependencies using uv:

```bash
uv sync
```

3. Set up your environment variables:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Usage

The CLI provides three main commands:

### Ask a single question

Ask a one-off question without conversation history:

```bash
uv run dspy-agent ask "What is the capital of France?"
```

With a custom model:

```bash
# Using OpenAI
uv run dspy-agent ask "What is the capital of France?" --model openai/gpt-4o

# Using Gemini 1.5 Pro
uv run dspy-agent ask "What is the capital of France?" --model gemini/gemini-1.5-pro
```

### Interactive chat mode with conversation history

Start a conversational session where the agent remembers context:

```bash
uv run dspy-agent chat
```

This starts an interactive session with conversation history management. The agent will remember all previous questions and answers in the session.

**Available commands in chat mode:**

- `history` - View the full conversation history in a formatted table
- `clear` - Reset the conversation history
- `exit`, `quit`, or `q` - End the session

**Example conversation:**

```
You: What is the capital of France?
Agent: The capital of France is Paris.

You: What is its population?
Agent: Paris has a population of approximately 2.1 million people in the city proper...

You: history
# Shows a table of all questions and answers

You: clear
Conversation history cleared!
```

View history at the end of session:

```bash
uv run dspy-agent chat --show-history
```

### Check version

```bash
uv run dspy-agent version
```

### MLflow Integration (Optional)

To enable tracing and evaluation with MLflow:

1. Start the MLflow server:

```bash
./scripts/start_mlflow.sh
```

2. Run commands with MLflow enabled:

```bash
# Ask with MLflow tracing
uv run dspy-agent ask "Find funds managed by BTG Pactual" --mlflow

# Chat with MLflow tracing
uv run dspy-agent chat --mlflow
```

3. View traces in the MLflow UI at `http://127.0.0.1:5001`

For more details, see [MLflow Integration Guide](docs/mlflow-integration.md) and [scripts/README.md](scripts/README.md).

## Configuration

### Environment Variables

Set these in your `.env` file:

1. **API Keys**:

   - `OPENAI_API_KEY`: Your OpenAI API key

2. **MLflow Settings** (optional):
   - `MLFLOW_ENABLED`: Set to `true` to enable MLflow tracing
   - `MLFLOW_TRACKING_URI`: MLflow server URL (e.g., `http://127.0.0.1:5001`)
   - `MLFLOW_EXPERIMENT_NAME`: Name for your MLflow experiment (defaults to `FundSearch-DSPy`)

### Command-line Options

- `--model` / `-m`: Specify the model to use (defaults to `gpt-4.1-mini`)
- `--api-key`: Provide API key directly (overrides environment variable)
- `--show-history`: (chat mode only) Show conversation history when exiting
- `--mlflow` / `--no-mlflow`: Enable or disable MLflow tracing

### Supported Models

The CLI uses OpenAI models. Common options:

- `gpt-4.1-mini` (default, fast and economical)
- `gpt-4o` (most capable)
- `gpt-4-turbo`

## How It Works

This CLI uses DSPy's conversation history management feature (`dspy.History`) to maintain context across chat sessions. Here's how it works:

1. **History Tracking**: Each question and answer is stored in a `dspy.History` object
2. **Context Awareness**: When you ask a follow-up question, the agent sees the full conversation history
3. **Smart Prompting**: DSPy formats the history as multi-turn messages for optimal model performance
4. **Flexible Modes**:
   - `ask` command: No history (good for one-off questions)
   - `chat` command: Full history (great for conversations)

## Project Structure

```
.
├── src/
│   ├── agent/                    # Agent orchestration
│   │   └── orchestrator.py      # ReAct-based fund search orchestrator
│   ├── cli/                     # CLI interface
│   │   ├── __init__.py
│   │   └── main.py              # CLI commands (ask, chat)
│   ├── tools/                   # DSPy tools
│   │   ├── tool_parse_query/    # Query parsing tool
│   │   └── tool_search_db/      # Database search tool
│   ├── infrastructure/          # Infrastructure code
│   │   ├── database/            # Database adapters and utilities
│   │   └── ingestion/           # Data ingestion scripts
│   ├── evaluation/              # Evaluation and optimization
│   │   ├── evaluate.py          # Evaluation scripts
│   │   └── optimize.py          # DSPy optimization
│   └── mlflow/                  # MLflow tracking data
│       ├── mlflow.db            # MLflow database
│       ├── mlruns/              # MLflow runs
│       └── mlartifacts/         # MLflow artifacts
├── scripts/                     # Helper scripts
│   ├── start_mlflow.sh          # Start MLflow server
│   └── README.md                # Scripts documentation
├── docs/                        # Documentation
│   └── mlflow-integration.md    # MLflow guide
├── pyproject.toml               # Project configuration
└── README.md
```

## Development

This project uses uv for dependency management. To add new dependencies:

```bash
uv add <package-name>
```

To run the CLI in development mode:

```bash
uv run dspy-agent
```

## License

MIT
