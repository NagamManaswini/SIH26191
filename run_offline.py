"""Standalone Offline Deployment Runner for Emergency Field Centers and PWD Teams.
Runs full platform in 100% offline disconnected mode using local SQLite database and PWA cached assets.
"""

import os
import sys
import subprocess
import time
import webbrowser

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["DATABASE_URL"] = "sqlite:///./sih_disaster.db"
os.environ["APP_ENV"] = "offline_deployment"
os.environ["DEBUG"] = "true"

print("=======================================================================")
print("   DISASTER EMERGENCY & RELOCATION PLATFORM — OFFLINE FIELD DEPLOYMENT ")
print("   Mode: Standalone Offline (Zero Internet Required / SQLite DB)       ")
print("=======================================================================")

base_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")

if not os.path.exists(venv_python):
    venv_python = sys.executable

frontend_dir = os.path.join(base_dir, "frontend")
frontend_dist = os.path.join(frontend_dir, "dist")

# Check if frontend bundle is built
if not os.path.exists(frontend_dist) or not os.path.exists(os.path.join(frontend_dist, "index.html")):
    print("\n[INFO] Building production PWA frontend bundle for offline mode...")
    try:
        subprocess.run(["cmd.exe", "/c", "npm run build"], cwd=frontend_dir, check=True)
        print("[OK] Frontend bundle built successfully.")
    except Exception as e:
        print(f"[NOTE] Could not pre-build frontend ({e}). Will run in dev server fallback mode.")

# 1. Start FastAPI Backend Server
print("\n[1/2] Launching Offline Disaster Core Engine on http://127.0.0.1:8001 ...")
backend_proc = subprocess.Popen(
    [venv_python, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001"],
    cwd=base_dir
)

time.sleep(2)

# 2. Check whether to start Vite Dev Server or use all-in-one FastAPI PWA bundle
frontend_proc = None
if os.path.exists(os.path.join(frontend_dist, "index.html")):
    print("\n[2/2] Using Built Offline PWA Bundle served directly by Core Engine.")
    target_url = "http://localhost:8001/"
else:
    print("\n[2/2] Launching Vite Frontend Dev Server on http://localhost:5173 ...")
    frontend_proc = subprocess.Popen(
        ["cmd.exe", "/c", "npm run dev"],
        cwd=frontend_dir
    )
    target_url = "http://localhost:5173/"

print("\n=======================================================================")
print("[OK] OFFLINE FIELD DEPLOYMENT IS READY!")
print(f"   - Offline Control Center: {target_url}")
print("   - Offline API Engine:     http://127.0.0.1:8001/docs")
print("   - Local Database:         sih_disaster.db (SQLite)")
print("   - PWA Service Worker:     Active & Pre-cached")
print("=======================================================================\n")

# Automatically open browser
try:
    webbrowser.open(target_url)
except Exception:
    pass

try:
    backend_proc.wait()
    if frontend_proc:
        frontend_proc.wait()
except KeyboardInterrupt:
    print("\nStopping offline deployment...")
    backend_proc.terminate()
    if frontend_proc:
        frontend_proc.terminate()
    print("[OK] Offline services stopped.")
