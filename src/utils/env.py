"""Environment variable validation - validates all required envs at startup."""

import os
from dataclasses import dataclass


class EnvValidationError(Exception):
    """Raised when required environment variables are missing."""

    pass


@dataclass
class Config:
    """Application configuration."""

    openai_api_key: str


REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
]


def validate_env() -> Config:
    """Validate all required environment variables at startup.

    Returns:
        Config with validated values

    Raises:
        EnvValidationError: If any required vars are missing
    """
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

    if missing:
        raise EnvValidationError(
            "Missing required environment variables:\n"
            + "\n".join(f"  - {var}" for var in missing)
            + "\n\nSet these in your .env file or environment."
        )

    return Config(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
