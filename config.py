"""Load configuration (secrets) from the .env file."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

REQUIRED_VARIABLES = ("GEMINI_API_KEY", "POSTGRES_URL")


class ConfigError(Exception):
    """Raised when a required environment variable is missing."""


@dataclass(frozen=True)
class Config:
    """Holds the settings the app needs."""

    gemini_api_key: str
    postgres_url: str


def load_config() -> Config:
    """Read the required variables from .env and return them as a Config."""
    load_dotenv()

    values = {}
    for name in REQUIRED_VARIABLES:
        value = os.getenv(name, "").strip()
        if not value:
            raise ConfigError(
                f"Missing environment variable: {name}. "
                f"Add it to your .env file (see .env.example)."
            )
        values[name] = value

    return Config(
        gemini_api_key=values["GEMINI_API_KEY"],
        postgres_url=values["POSTGRES_URL"],
    )
