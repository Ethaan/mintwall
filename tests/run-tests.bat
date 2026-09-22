@echo off
rem Runs the gameplay test suite against an isolated test server (port 7181, tests\.run\test.db3).
rem   tests\run-tests.bat                 all tests
rem   tests\run-tests.bat -k oracle       only tests matching "oracle"
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv || python -m venv .venv || exit /b 1
  .venv\Scripts\python.exe -m pip install -q -r requirements.txt || exit /b 1
)
.venv\Scripts\python.exe -m pytest %*
