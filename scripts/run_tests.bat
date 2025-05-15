@echo off
cd %~dp0..
echo Running tests with config from config/pytest.ini...
pytest -c config/pytest.ini
pause
