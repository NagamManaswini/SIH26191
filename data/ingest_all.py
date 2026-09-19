"""Alias launcher for src/data/ingest_all.py."""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.ingest_all import run_ingestion_pipeline

if __name__ == "__main__":
    run_ingestion_pipeline()
