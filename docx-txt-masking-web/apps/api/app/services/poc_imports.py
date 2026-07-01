from __future__ import annotations

import sys

from app.core.config import settings


core_path = str(settings.poc_core_dir)
if core_path not in sys.path:
    sys.path.insert(0, core_path)
