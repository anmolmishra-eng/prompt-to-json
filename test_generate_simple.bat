@echo off
chcp 65001 >nul

echo ============================================================
echo 🎨 CURL TEST: /api/v1/generate Endpoint
echo ============================================================
echo.

set BASE_URL=http://127.0.0.1:8000

:: Step 1: Register (may fail if user exists - that's OK)
echo [1/4] Registering user...
curl -X POST "%BASE_URL%/api/v1/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"admin\",\"full_name\":\"Admin User\"}" ^
  -s -o nul -w "Status: %%{http_code}\n"

echo.

:: Step 2: Login and save response
echo [2/4] Logging in...
curl -X POST "%BASE_URL%/api/v1/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=admin&password=admin" ^
  -s -o login.json -w "Status: %%{http_code}\n"

echo.

:: Step 3: Extract token and test generate
echo [3/4] Calling /api/v1/generate...
echo.
echo Request:
echo   POST %BASE_URL%/api/v1/generate
echo   Body: {
echo     "user_id": "admin",
echo     "prompt": "Design a 3-bedroom residential building in Mumbai with 2000 sq ft area",
echo     "project_id": "proj_001",
echo     "context": {"city": "Mumbai", "plot_area": 2000, "building_type": "residential"}
echo   }
echo.

:: Get token from login.json
for /f "tokens=2 delims=:," %%a in ('type login.json ^| findstr "access_token"') do (
    set TOKEN=%%a
    set TOKEN=!TOKEN:"=!
    set TOKEN=!TOKEN: =!
)

curl -X POST "%BASE_URL%/api/v1/generate" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"admin\",\"prompt\":\"Design a 3-bedroom residential building in Mumbai with 2000 sq ft area\",\"project_id\":\"proj_001\",\"context\":{\"city\":\"Mumbai\",\"plot_area\":2000,\"building_type\":\"residential\"}}" ^
  -s -o generate.json -w "\nHTTP Status: %%{http_code}\n"

echo.

:: Step 4: Display result
echo [4/4] Response:
echo ============================================================
type generate.json
echo.
echo ============================================================

echo.
echo Files created:
echo   - login.json (authentication response)
echo   - generate.json (generate endpoint response)
echo.

pause
