@echo off
echo Setting up documentation...
echo.

echo 1. Installing dependencies...
pip install -r ..\..\requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    pause
    exit /b 1
)

echo.
echo 2. Building documentation...
make.bat html
if %errorlevel% neq 0 (
    echo Error building documentation!
    pause
    exit /b 1
)

echo.
echo 3. Documentation built successfully!
echo You can view it by running: start _build\html\index.html
echo Or serve it locally with: cd _build\html && python -m http.server 8000
echo.
pause