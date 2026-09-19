import sys
import os
import importlib

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_root_dir = os.path.dirname(_backend_dir)
for _p in [_root_dir, _backend_dir]:
    if _p and os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from backend.app.main import app
except ImportError:
    # Fallback for serverless environments where backend directory is root
    _mod = importlib.import_module("app.main")
    app = getattr(_mod, "app")
