import os
import sys

# Robust sys.path resolution supporting all Vercel/AWS Lambda directory structures
_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
_grandparent = os.path.dirname(_parent)
_cwd = os.getcwd()

for _base in [_here, _parent, _grandparent, _cwd, "/var/task"]:
    if _base and os.path.exists(_base):
        if _base not in sys.path:
            sys.path.insert(0, _base)
        _backend_candidate = os.path.join(_base, "backend")
        if os.path.exists(_backend_candidate) and _backend_candidate not in sys.path:
            sys.path.insert(0, _backend_candidate)

try:
    from backend.app.main import app
except ModuleNotFoundError:
    try:
        from app.main import app
    except ModuleNotFoundError:
        import importlib
        _mod = importlib.import_module("backend.app.main")
        app = getattr(_mod, "app")

# Top-level ASGI FastAPI instance for Vercel serverless execution
app = app

__all__ = ["app"]
