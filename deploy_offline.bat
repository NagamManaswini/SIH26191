@echo off
title Disaster Management Platform - PWD & Offline Field Deployment
color 0A

echo =======================================================================
echo    DISASTER PLATFORM: PWD / EMERGENCY FIELD OFFLINE LAUNCHER
echo =======================================================================
echo.
echo [1/3] Setting offline environment configuration...
set DATABASE_URL=sqlite:///./sih_disaster.db
set APP_ENV=offline_deployment
set DEBUG=true

echo [2/3] Checking Python virtual environment...
if exist .venv\Scripts\python.exe (
    set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
    set PYTHON_EXEC=python
)

echo [3/3] Starting Standalone Offline Engine & PWA Portal...
echo.
%PYTHON_EXEC% run_offline.py

pause
