import os
import mlflow

def setup_mlflow(
    experiment_name: str = "FundSearch-Agent",
    tracking_uri: str | None = None
) -> None:
    """
    Configure MLflow tracing.
    
    Args:
        experiment_name: Name of the MLflow experiment.
        tracking_uri: Optional tracking URI. If not provided, checks env var or defaults to localhost.
    """
    tracking_uri = tracking_uri or os.getenv(
        "MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"
    )
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    mlflow.openai.autolog()

