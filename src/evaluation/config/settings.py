import os

from dotenv import load_dotenv

from src.utils.env import validate_env

# Load environment variables
load_dotenv()

# Validate environment to ensure API keys are present
env_config = validate_env()

# Constants
OPENAI_API_KEY = env_config.openai_api_key
MLFLOW_ENABLED = os.getenv("MLFLOW_ENABLED", "false").lower() == "true"
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "src/mlflow/mlflow.db")
MLFLOW_EXPERIMENT_NAME = "FundSearch-Evaluation"

# Model Configuration
DEFAULT_MODEL = "openai/gpt-4o-mini"
REFLECTION_MODEL = "openai/gpt-4.1"  # Stronger model for optimization reflection

# Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
