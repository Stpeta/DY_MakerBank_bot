"""Package initialization for configuration.

This module loads the application configuration once and exposes the
resulting ``config`` object for import throughout the project.
"""

from .config import load_config

# Load configuration at import time to avoid repeated parsing of the
# environment variables across the codebase.
config = load_config()

__all__ = ["config"]

