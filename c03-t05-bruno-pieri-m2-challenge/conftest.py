"""
conftest.py — pytest session setup for the M2 capstone.

Changes the working directory to the capstone root so that relative paths
(data/, chroma_db/) resolve correctly regardless of where pytest is invoked.
Also loads the .env file from the project hierarchy so OPENAI_API_KEY is set.
"""

import os
from pathlib import Path

import pytest


# Directory containing this conftest.py (= capstone root)
_CAPSTONE_ROOT = Path(__file__).parent.resolve()


def pytest_configure(config):
    """Change CWD to capstone root and load environment variables."""
    os.chdir(_CAPSTONE_ROOT)

    # Load .env from capstone root first, then search parent dirs
    from dotenv import load_dotenv, find_dotenv
    dotenv_path = find_dotenv(usecwd=False)
    if dotenv_path:
        load_dotenv(dotenv_path, override=False)
