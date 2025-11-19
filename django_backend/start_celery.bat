@echo off
REM Start Celery worker for Windows
echo Starting Celery worker...
celery -A config worker --loglevel=info --pool=solo
pause
