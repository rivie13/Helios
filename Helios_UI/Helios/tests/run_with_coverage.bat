@echo off
REM Run tests with coverage
cd ..\..
python -m pytest Helios/tests/ --cov=Helios --cov-report=html --cov-report=term --cov-config=.coveragerc

REM Open the coverage report
start htmlcov\index.html

echo.
echo Coverage report generated in htmlcov directory 