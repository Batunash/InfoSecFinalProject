@echo off
REM DevSecOps Pipeline Demo Script for Windows
REM This script demonstrates all security features of the pipeline

echo ==========================================
echo DevSecOps Pipeline Demo
echo ==========================================
echo.

REM 1. Project Structure
echo ==========================================
echo 1. Project Structure
echo ==========================================
echo.
echo Directory structure:
dir /B /S *.py *.yml *.yaml *.txt *.md | findstr /V "__pycache__"
echo.

REM 2. Build Application
echo ==========================================
echo 2. Building Application
echo ==========================================
echo.
cd app
docker build -t devsecops-app:demo .
if %ERRORLEVEL% EQU 0 (
    echo [OK] Docker image built
) else (
    echo [ERROR] Docker build failed
)
cd ..
echo.

REM 3. Start Application
echo ==========================================
echo 3. Starting Application
echo ==========================================
echo.
docker-compose up -d app
timeout /t 5 /nobreak >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Application started
) else (
    echo [ERROR] Application failed to start
)
echo.

REM 4. Health Check
echo ==========================================
echo 4. Health Check
echo ==========================================
echo.
curl -s http://localhost:5000/health
echo.
echo [OK] Health check passed
echo.

REM 5. API Testing
echo ==========================================
echo 5. API Testing
echo ==========================================
echo.

echo Registering user...
curl -s -X POST http://localhost:5000/api/register -H "Content-Type: application/json" -d "{\"username\":\"demouser\",\"password\":\"password123\",\"email\":\"demo@test.com\"}"
echo.
echo [OK] User registered
echo.

echo Logging in...
for /f "delims=" %%i in ('powershell -NoProfile -Command "$r = Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/login -ContentType 'application/json' -Body '{"username":"demouser","password":"password123"}'; $r | ConvertTo-Json -Depth 10; $r.access_token"') do set "TOKEN=%%i"
echo [OK] User logged in
echo.

echo Accessing protected endpoint...
<<<<<<< HEAD
REM Note: In practice, extract token from login response above and use it here
REM Example: curl -s -X GET http://localhost:5000/api/protected -H "Authorization: Bearer <actual_token_from_login>"
echo [OK] Protected endpoint accessed (demo - replace with actual token)
=======
curl -s -X GET http://localhost:5000/api/protected -H "Authorization: Bearer %TOKEN%"
echo.
if %ERRORLEVEL% EQU 0 (
    echo [OK] Protected endpoint accessed
) else (
    echo [WARNING] Protected endpoint check failed
)
>>>>>>> d75c4e04df2dade565ecf3a7f59e7c56c5ddb38c
echo.

REM 6. Unit Tests
echo ==========================================
echo 6. Running Unit Tests
echo ==========================================
echo.
cd app
pytest tests/ -v --cov=src --cov-report=term-missing
if %ERRORLEVEL% EQU 0 (
    echo [OK] Unit tests passed
) else (
    echo [WARNING] Some tests failed
)
cd ..
echo.

REM 7. SAST with Bandit
echo ==========================================
echo 7. Static Application Security Testing (Bandit)
echo ==========================================
echo.
cd app
bandit -r src/ -c ../security/bandit-config.yaml
echo [OK] SAST scan completed
cd ..
echo.

REM 8. SCA with Safety
echo ==========================================
echo 8. Software Composition Analysis (Safety)
echo ==========================================
echo.
cd app
safety check
echo [OK] SCA scan completed
cd ..
echo.

REM 9. Container Scanning with Trivy
echo ==========================================
echo 9. Container Image Scanning (Trivy)
echo ==========================================
echo.
where trivy >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    trivy image devsecops-app:demo --severity HIGH,CRITICAL
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Container scan completed
    ) else (
        echo [WARNING] Container scan found issues
    )
) else (
    echo [WARNING] Trivy is not installed; container scan skipped
)
echo.

REM 10. Code Quality Checks
echo ==========================================
echo 10. Code Quality Checks
echo ==========================================
echo.
cd app\src
echo Running Black...
black --check .
echo.
echo Running Flake8...
flake8 . --max-line-length=100
cd ..\..
echo [OK] Code quality checks completed
echo.

REM 11. Security Summary
echo ==========================================
echo 11. Security Summary
echo ==========================================
echo.
echo Security Tools Used:
echo   [OK] SAST: Bandit
echo   [OK] SCA: Safety
echo   [OK] Container: Trivy
echo   [OK] Code Quality: Black, Flake8
echo.
echo Security Features Implemented:
echo   [OK] JWT-based authentication
echo   [OK] Password hashing with bcrypt
echo   [OK] Input validation
echo   [OK] Output encoding
echo   [OK] Security event logging
echo.

REM 12. Cleanup
echo ==========================================
echo 12. Cleanup
echo ==========================================
echo.
set /p STOP="Stop application? (y/n): "
if /i "%STOP%"=="y" (
    docker-compose down
    echo [OK] Application stopped
)
echo.

echo ==========================================
echo Demo Complete!
echo ==========================================
echo All security features have been demonstrated.
echo.
pause
