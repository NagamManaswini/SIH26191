#!/usr/bin/env bash
# Disaster Management Platform - PWD & Offline Field Deployment Script

echo "======================================================================="
echo "   DISASTER PLATFORM: PWD / EMERGENCY FIELD OFFLINE LAUNCHER"
echo "======================================================================="
echo ""

export DATABASE_URL="sqlite:///./sih_disaster.db"
export APP_ENV="offline_deployment"
export DEBUG="true"

if [ -f ".venv/bin/python" ]; then
    PYTHON_EXEC=".venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_EXEC="python3"
else
    PYTHON_EXEC="python"
fi

echo "[INFO] Running offline launcher using $PYTHON_EXEC..."
$PYTHON_EXEC run_offline.py
