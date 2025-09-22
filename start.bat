@echo off
echo ========================================
echo  Smart CV Management Platform Setup
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting the platform...
python run.py
pause
