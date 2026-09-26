import os
import sys

# Configure sys.path so backend package is discoverable
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_backend_dir = os.path.join(_root_dir, "backend")

for _p in [_root_dir, _backend_dir]:
    if _p and os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from backend.app.main import app  # noqa: F401

__all__ = ["app"]

