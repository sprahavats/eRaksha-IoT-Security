"""Shared paths and configuration for the eRaksha prototype."""

from pathlib import Path

# Project root: eRaksha-IoT-Security/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "eraksha.db"

# This prototype uses simulated traffic by default.
DEFAULT_DETECTION_THRESHOLD = 0.65
MIN_TRAINING_SAMPLES = 50
RANDOM_STATE = 42