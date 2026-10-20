"""Shared fake input and safe environment loading for the demos."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent

POD_SUMMARY = (
    "Pod Atlas: 20-day return -3.2%; max drawdown 6.8%; "
    "volatility 1.7x baseline."
)


def load_project_env() -> None:
    """Load local credentials without overwriting shell-provided values."""
    load_dotenv(PROJECT_ROOT / ".env.local", override=False)


def require_env(name: str) -> None:
    """Exit with a useful message without ever displaying a secret."""
    if not os.environ.get(name):
        raise SystemExit(
            f"Missing {name}. Add it to {PROJECT_ROOT / '.env.local'} "
            "and rerun this demo."
        )
