"""CLI interface for the DSPy agent."""

import os

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.agent.orchestrator import FundSearchOrchestrator
from src.utils.env import EnvValidationError, validate_env

# Load environment variables
load_dotenv()

DEFAULT_MODEL = "gpt-4.1-mini"

app = typer.Typer(
    name="dspy-agent",
    help="A CLI for interacting with DSPy agents with conversation history",
    add_completion=False,
)
console = Console()


@app.command()
def ask(
    question: str = typer.Argument(..., help="The question to ask the agent"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="OpenAI model to use"),
    api_key: str | None = typer.Option(None, "--api-key", help="OpenAI API key (overrides env)"),
    enable_mlflow: bool = typer.Option(False, "--mlflow/--no-mlflow", help="Enable MLflow tracing"),
):
    """Ask the agent a single question without conversation history."""
    try:
        # Get API key from argument or environment
        if not api_key:
            config = validate_env()
            api_key = config.openai_api_key

        # Get MLflow configuration from environment if enabled
        mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI") if enable_mlflow else None
        mlflow_experiment_name = (
            os.getenv("MLFLOW_EXPERIMENT_NAME", "FundSearch-DSPy")
            if enable_mlflow
            else "FundSearch-DSPy"
        )

        agent = FundSearchOrchestrator(
            api_key=api_key,
            model=model,
            enable_mlflow=enable_mlflow,
            mlflow_tracking_uri=mlflow_tracking_uri,
            mlflow_experiment_name=mlflow_experiment_name,
        )

        with console.status("[bold green]Thinking...", spinner="dots"):
            answer = agent.ask(question, use_history=False)

        console.print(Panel(answer, title="[bold blue]Answer", border_style="blue"))

    except EnvValidationError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def chat(
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="OpenAI model to use"),
    api_key: str | None = typer.Option(None, "--api-key", help="OpenAI API key (overrides env)"),
    show_history: bool = typer.Option(
        False, "--show-history", help="Show conversation history at the end"
    ),
    enable_mlflow: bool = typer.Option(False, "--mlflow/--no-mlflow", help="Enable MLflow tracing"),
):
    """Start an interactive chat session with the agent.

    Maintains conversation history across all messages in the session.
    Use 'history' to view the conversation, 'clear' to reset, or 'exit'/'quit'/'q' to end.
    """
    try:
        # Get API key from argument or environment
        if not api_key:
            config = validate_env()
            api_key = config.openai_api_key

        # Get MLflow configuration from environment if enabled
        mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI") if enable_mlflow else None
        mlflow_experiment_name = (
            os.getenv("MLFLOW_EXPERIMENT_NAME", "FundSearch-DSPy")
            if enable_mlflow
            else "FundSearch-DSPy"
        )

        # Clear MLflow tracking URI if using local file storage
        if enable_mlflow and not mlflow_tracking_uri and "MLFLOW_TRACKING_URI" in os.environ:
            del os.environ["MLFLOW_TRACKING_URI"]

        agent = FundSearchOrchestrator(
            api_key=api_key,
            model=model,
            enable_mlflow=enable_mlflow,
            mlflow_tracking_uri=mlflow_tracking_uri,
            mlflow_experiment_name=mlflow_experiment_name,
        )
        console.print(
            Panel(
                "[bold green]Chat started with conversation history![/bold green]\n\n"
                "Commands:\n"
                "  • Type 'history' to view conversation history\n"
                "  • Type 'clear' to reset conversation history\n"
                "  • Type 'exit', 'quit', or 'q' to end the session",
                title="[bold blue]DSPy Agent Chat",
                border_style="blue",
            )
        )

        while True:
            try:
                question = console.input("\n[bold cyan]You:[/bold cyan] ")

                if question.lower() in ["exit", "quit", "q"]:
                    if show_history:
                        display_history(agent)
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if not question.strip():
                    continue

                # Special commands
                if question.lower() == "history":
                    display_history(agent)
                    continue

                if question.lower() == "clear":
                    agent.reset_history()
                    console.print("[yellow]Conversation history cleared![/yellow]")
                    continue

                with console.status("[bold green]Thinking...", spinner="dots"):
                    answer = agent.chat(question)

                console.print(f"[bold green]Agent:[/bold green] {answer}")
            except KeyboardInterrupt:
                if show_history:
                    display_history(agent)
                console.print("\n[yellow]Goodbye![/yellow]")
                break
    except EnvValidationError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from None


def display_history(agent: FundSearchOrchestrator):
    """Display the conversation history in a formatted table."""
    history = agent.get_history()

    if not history:
        console.print("[yellow]No conversation history yet.[/yellow]")
        return

    table = Table(title="Conversation History", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Question", style="cyan")
    table.add_column("Answer", style="green")

    for idx, turn in enumerate(history, 1):
        table.add_row(str(idx), turn.get("question", ""), turn.get("answer", ""))

    console.print(table)


@app.command()
def version():
    """Show the version of the CLI."""
    from . import __version__

    console.print(f"DSPy Agent CLI version: [bold blue]{__version__}[/bold blue]")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
