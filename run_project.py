import subprocess
import sys
import time
import os

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

print("==========================================================")
print(" STARTING DISASTER MANAGEMENT & RELOCATION PLATFORM")
print("==========================================================")

base_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")

if not os.path.exists(venv_python):
    venv_python = sys.executable

# 1. Start FastAPI Backend Server
print("\n[1/2] Launching FastAPI Backend Server on http://127.0.0.1:8001 ...")
backend_proc = subprocess.Popen(
    [venv_python, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8001", "--reload"],
    cwd=base_dir
)

time.sleep(2)

# 2. Start Vite Frontend Dev Server
frontend_dir = os.path.join(base_dir, "frontend")
print("\n[2/2] Launching Vite Frontend Dev Server on http://localhost:5173 ...")
frontend_proc = subprocess.Popen(
    ["cmd.exe", "/c", "npm run dev"],
    cwd=frontend_dir
)

print("\n==========================================================")
print("[OK] BOTH SERVICES ARE RUNNING!")
print("   - Frontend UI: http://localhost:5173/")
print("   - Backend API: http://127.0.0.1:8001/docs")
print("Press CTRL+C in this terminal to stop both servers.")
print("==========================================================\n")

try:
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    print("\nStopping servers...")
    backend_proc.terminate()
    frontend_proc.terminate()
    print("Done.")

