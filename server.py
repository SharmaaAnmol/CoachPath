#!/usr/bin/env python3
"""
CoachPath Launcher
Build for Bharat Hackathon 2.0 · AI-powered Career Intelligence & Job Application Assistant
"""
import sys
from pathlib import Path

# Ensure backend modules are on PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.core.config import settings
from app.local_server import run_server

if __name__ == "__main__":
    port = settings.PORT or 8000
    run_server(port)
