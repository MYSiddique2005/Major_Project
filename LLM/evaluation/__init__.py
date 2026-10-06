"""Phase 8: evaluation of the IntelliERP assistant. See LLM/README.md.

Importing this package makes the backend importable and runs from the backend's folder, because the
evaluation uses the application's own code and the settings in Backend/.env.
"""
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2] / "Backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)
