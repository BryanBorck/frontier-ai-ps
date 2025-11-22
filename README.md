# DSPy Agent CLI

A command-line interface for interacting with DSPy agents with conversation history management. This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management and [DSPy](https://github.com/stanfordnlp/dspy) for building language model programs.

## Features

- 🤖 **Conversation History**: Maintains context across chat sessions using DSPy's History utility
- 💬 **Interactive Chat Mode**: Have natural conversations with the agent
- ❓ **Single-Question Mode**: Ask one-off questions without history
- 🎨 **Rich Terminal UI**: Beautiful interface with tables, panels, and syntax highlighting
- 🔧 **Flexible Model Support**: Works with Gemini, OpenAI, and other LiteLLM-supported models
- 📊 **History Commands**: View and manage conversation history in real-time
- 🌍 **Environment-based Configuration**: Easy setup with .env files

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
# Edit .env and add your GEMINI_API_KEY (or GOOGLE_API_KEY or OPENAI_API_KEY)
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

## Configuration

### Environment Variables

Set these in your `.env` file:

1. **API Keys** (you only need one):
   - `GEMINI_API_KEY`: Your Google Gemini API key (recommended)
   - `GOOGLE_API_KEY`: Alternative to GEMINI_API_KEY
   - `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI models)

2. **Optional Settings**:
   - `MODEL`: Default model to use (defaults to `gemini/gemini-2.0-flash-exp`)

### Command-line Options

- `--model` / `-m`: Specify the model to use
- `--api-key`: Provide API key directly (overrides environment variable)
- `--show-history`: (chat mode only) Show conversation history when exiting

### Supported Models

The CLI supports any model available through [LiteLLM](https://docs.litellm.ai/docs/providers). Common options:

**Gemini (Google):**
- `gemini/gemini-2.0-flash-exp` (default, fastest)
- `gemini/gemini-1.5-pro` (most capable)
- `gemini/gemini-1.5-flash` (balanced)

**OpenAI:**
- `openai/gpt-4o` (most capable)
- `openai/gpt-4.1-mini` (fast and economical)
- `openai/gpt-4-turbo`

**And many more!** Check [LiteLLM docs](https://docs.litellm.ai/docs/providers) for the full list.

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
│   └── cli/
│       ├── __init__.py
│       ├── main.py      # CLI interface with history commands
│       └── agent.py     # DSPy agent with conversation history
├── pyproject.toml       # Project configuration
├── .env.example         # Example environment variables
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