"""Configuration loading: domain YAML + environment variables.

Two sources, one order:
  1. config/domains/<domain>.yaml — what changes per domain.
  2. .env (environment variables) — secrets and machine settings.
The domain file never holds secrets; the environment never holds taxonomy.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
DOMAINS_DIR = REPO_ROOT / "config" / "domains"


def load_env() -> None:
    """Load .env into os.environ (no-op if the file is missing)."""
    load_dotenv(REPO_ROOT / ".env")


def load_domain(domain: str) -> dict:
    """Load and minimally validate config/domains/<domain>.yaml."""
    path = DOMAINS_DIR / f"{domain}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"no domain config for {domain!r} at {path}")
    with path.open() as f:
        config = yaml.safe_load(f)
    for key in ("domain", "source_filter", "skill_taxonomy", "seniority"):
        if key not in config:
            raise ValueError(f"domain config {path} is missing top-level key {key!r}")
    return config


def get_env(name: str, default: str | None = None) -> str:
    """Read one environment variable, failing loudly when required."""
    value = os.environ.get(name, default)
    if value is None:
        raise ValueError(f"required environment variable {name!r} is not set")
    return value
