@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo 🎨 TESTING /api/v1/generate ENDPOINT WITH CURL
echo ============================================================

set BASE_URL=http://127.0.0.1:8000
set TOKEN=

echo.
echo 1️⃣ STEP 1: Register Admin User
echo ============================================================
curl -X POST "%BASE_URL%/api/v1/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"admin\",\"full_name\":\"Admin User\"}" ^
  -w "\nStatus: %%{http_code}\n" ^
  -s

echo.
echo.
echo 2️⃣ STEP 2: Login and Get Token
echo ============================================================
for /f "delims=" %%i in ('curl -X POST "%BASE_URL%/api/v1/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=admin" -s') do set LOGIN_RESPONSE=%%i

echo Response: %LOGIN_RESPONSE%

:: Extract token using PowerShell
for /f "delims=" %%i in ('powershell -Command "$json = '%LOGIN_RESPONSE%' | ConvertFrom-Json; $json.access_token"') do set TOKEN=%%i

if "%TOKEN%"=="" (
    echo ❌ Failed to get token
    exit /b 1
)

echo ✅ Token obtained: %TOKEN:~0,30%...

echo.
echo.
echo 3️⃣ STEP 3: Test Generate Endpoint
echo ============================================================
echo Request Body:
echo {
echo   "user_id": "admin",
echo   "prompt": "Design a 3-bedroom residential building in Mumbai with 2000 sq ft area",
echo   "project_id": "proj_001",
echo   "context": {
echo     "city": "Mumbai",
echo     "plot_area": 2000,
echo     "building_type": "residential"
echo   }
echo }
echo.

curl -X POST "%BASE_URL%/api/v1/generate" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"admin\",\"prompt\":\"Design a 3-bedroom residential building in Mumbai with 2000 sq ft area\",\"project_id\":\"proj_001\",\"context\":{\"city\":\"Mumbai\",\"plot_area\":2000,\"building_type\":\"residential\"}}" ^
  -w "\n\n📊 HTTP Status: %%{http_code}\n" ^
  -v ^
  -o generate_response.json

echo.
echo.
echo 4️⃣ STEP 4: Display Response
echo ============================================================
type generate_response.json
echo.

echo.
echo.
echo 5️⃣ STEP 5: Extract and Verify Spec ID
echo ============================================================
for /f "delims=" %%i in ('powershell -Command "if (Test-Path generate_response.json) { $json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.spec_id) { Write-Output $json.spec_id } }"') do set SPEC_ID=%%i

if not "%SPEC_ID%"=="" (
    echo ✅ Spec ID: %SPEC_ID%

    echo.
    echo 6️⃣ STEP 6: Retrieve Generated Spec
    echo ============================================================
    curl -X GET "%BASE_URL%/api/v1/specs/%SPEC_ID%" ^
      -H "Authorization: Bearer %TOKEN%" ^
      -w "\n\n📊 HTTP Status: %%{http_code}\n" ^
      -s
) else (
    echo ⚠️ No spec_id found in response
)

echo.
echo.
echo ============================================================
echo ✅ TEST COMPLETED
echo ============================================================
echo Response saved to: generate_response.json
echo.

endlocal
