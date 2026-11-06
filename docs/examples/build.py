"""Install the example skill into the conda build prefix."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

source = Path(__file__).parent / "review-notes"
destination = Path(os.environ["PREFIX"]) / "share/agent-skills/review-notes"
shutil.copytree(source, destination)
