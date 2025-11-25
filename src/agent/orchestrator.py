"""ReAct-based agent orchestrator for fund search."""

import dspy

import mlflow
from src.tools.tool_parse_query.index import _FundQueryParserInternal
from src.tools.tool_search_db.index import _FundSearchInternal
from src.tools.tool_semantic_search.index import _FundSemanticSearchInternal
from src.tools.tool_web_search.index import _WebSearchInternal


class FundSearchOrchestrator:
    """ReAct agent that orchestrates fund search using DSPy tools."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
        mlflow_tracking_uri: str | None = None,
        mlflow_experiment_name: str = "FundSearch-DSPy",
        enable_mlflow: bool = False,
    ):
        """Initialize the ReAct orchestrator.

        Args:
            api_key: OpenAI API key
            model: The OpenAI model to use
            mlflow_tracking_uri: MLflow tracking server URI (e.g., "http://127.0.0.1:5000")
            mlflow_experiment_name: Name for the MLflow experiment
            enable_mlflow: Whether to enable MLflow tracing (default: False)
        """
        # Configure MLflow if enabled
        if enable_mlflow:
            try:
                if mlflow_tracking_uri:
                    mlflow.set_tracking_uri(mlflow_tracking_uri)
                # Enable automatic logging of DSPy traces (must be called before set_experiment)
                mlflow.dspy.autolog()
                # Set experiment name
                mlflow.set_experiment(mlflow_experiment_name)
            except Exception as e:
                print(f"Warning: Failed to initialize MLflow: {e}")
                print("Continuing without MLflow tracing...")

        self.lm = dspy.LM(model=f"openai/{model}", api_key=api_key)
        dspy.configure(lm=self.lm)

        self.history = dspy.History(messages=[])
        self.last_result = None

        # Initialize tools from tools folder
        # Note: Using internal classes for ReAct compatibility
        parser = _FundQueryParserInternal()
        searcher = _FundSearchInternal()
        semantic_searcher = _FundSemanticSearchInternal()
        web_searcher = _WebSearchInternal()

        # Create ReAct agent with tools
        self.agent = dspy.ReAct(
            signature="question -> answer",
            tools=[
                parser.parse,
                searcher.search_db,
                semantic_searcher.search_semantic,
                web_searcher.web_search,
            ],
            max_iters=5,
        )

    def ask(self, question: str, use_history: bool = False) -> str:
        """Ask the agent a question.

        Args:
            question: The question to ask
            use_history: Whether to use conversation history

        Returns:
            The agent's answer
        """
        # Get answer from ReAct agent
        result = self.agent(question=question)
        self.last_result = result
        answer = result.answer

        # Add to history if requested
        if use_history:
            self.history.messages.append({"question": question, "answer": answer})

        return answer

    def chat(self, message: str) -> str:
        """Send a message to the agent in a conversational context."""
        return self.ask(message, use_history=True)

    def reset_history(self):
        """Reset the conversation history."""
        self.history = dspy.History(messages=[])

    def get_history(self) -> list[dict]:
        """Get the current conversation history."""
        return self.history.messages

    def get_last_result(self):
        """Get the result from the last agent execution (includes trajectory)."""
        return self.last_result
