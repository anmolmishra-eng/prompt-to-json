@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Configuration
set BASE_URL=http://127.0.0.1:8000
set USERNAME=admin
set PASSWORD=admin
set EMAIL=admin@example.com

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     🎨 COMPREHENSIVE /api/v1/generate ENDPOINT TEST       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: ============================================================
:: STEP 1: REGISTER USER
:: ============================================================
echo ┌────────────────────────────────────────────────────────────┐
echo │ STEP 1: Register Admin User                               │
echo └────────────────────────────────────────────────────────────┘
echo.
echo Endpoint: POST %BASE_URL%/api/v1/auth/register
echo Body: {"username":"%USERNAME%","email":"%EMAIL%","password":"***","full_name":"Admin User"}
echo.

curl -X POST "%BASE_URL%/api/v1/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"%USERNAME%\",\"email\":\"%EMAIL%\",\"password\":\"%PASSWORD%\",\"full_name\":\"Admin User\"}" ^
  -s -o register_response.json -w "HTTP Status: %%{http_code}\n"

echo Response saved to: register_response.json
echo.

:: ============================================================
:: STEP 2: LOGIN
:: ============================================================
echo ┌────────────────────────────────────────────────────────────┐
echo │ STEP 2: Login and Obtain Access Token                     │
echo └────────────────────────────────────────────────────────────┘
echo.
echo Endpoint: POST %BASE_URL%/api/v1/auth/login
echo Body: username=%USERNAME%^&password=***
echo.

curl -X POST "%BASE_URL%/api/v1/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=%USERNAME%&password=%PASSWORD%" ^
  -s -o login_response.json -w "HTTP Status: %%{http_code}\n"

echo Response saved to: login_response.json
echo.

:: Extract token
for /f "tokens=2 delims=:," %%a in ('type login_response.json ^| findstr "access_token"') do (
    set TOKEN=%%a
    set TOKEN=!TOKEN:"=!
    set TOKEN=!TOKEN: =!
)

if "!TOKEN!"=="" (
    echo ❌ ERROR: Failed to obtain access token
    echo.
    echo Login Response:
    type login_response.json
    echo.
    pause
    exit /b 1
)

echo ✅ Token obtained successfully
echo Token (first 40 chars): !TOKEN:~0,40!...
echo.

:: ============================================================
:: STEP 3: GENERATE DESIGN
:: ============================================================
echo ┌────────────────────────────────────────────────────────────┐
echo │ STEP 3: Generate Design Specification                     │
echo └────────────────────────────────────────────────────────────┘
echo.
echo Endpoint: POST %BASE_URL%/api/v1/generate
echo Headers:
echo   - Authorization: Bearer !TOKEN:~0,30!...
echo   - Content-Type: application/json
echo.
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
echo ⏳ Sending request... (this may take 5-15 seconds)
echo.

curl -X POST "%BASE_URL%/api/v1/generate" ^
  -H "Authorization: Bearer !TOKEN!" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"admin\",\"prompt\":\"Design a 3-bedroom residential building in Mumbai with 2000 sq ft area\",\"project_id\":\"proj_001\",\"context\":{\"city\":\"Mumbai\",\"plot_area\":2000,\"building_type\":\"residential\"}}" ^
  -s -o generate_response.json -w "HTTP Status: %%{http_code}\n" ^
  --max-time 60

echo.
echo Response saved to: generate_response.json
echo.

:: ============================================================
:: STEP 4: ANALYZE RESPONSE
:: ============================================================
echo ┌────────────────────────────────────────────────────────────┐
echo │ STEP 4: Analyze Response                                  │
echo └────────────────────────────────────────────────────────────┘
echo.

if not exist generate_response.json (
    echo ❌ ERROR: Response file not created
    pause
    exit /b 1
)

echo Response Content:
echo ════════════════════════════════════════════════════════════
type generate_response.json
echo.
echo ════════════════════════════════════════════════════════════
echo.

:: Extract key fields using PowerShell
echo Extracting key information...
echo.

powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.spec_id) { Write-Output \"✅ spec_id: $($json.spec_id)\" } else { Write-Output \"❌ spec_id: NOT FOUND\" }"
powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.estimated_cost) { Write-Output \"✅ estimated_cost: ₹$($json.estimated_cost)\" } else { Write-Output \"❌ estimated_cost: NOT FOUND\" }"
powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.preview_url) { Write-Output \"✅ preview_url: $($json.preview_url)\" } else { Write-Output \"❌ preview_url: NOT FOUND\" }"
powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.compliance_check_id) { Write-Output \"✅ compliance_check_id: $($json.compliance_check_id)\" } else { Write-Output \"❌ compliance_check_id: NOT FOUND\" }"
powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.created_at) { Write-Output \"✅ created_at: $($json.created_at)\" } else { Write-Output \"❌ created_at: NOT FOUND\" }"
powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.spec_version) { Write-Output \"✅ spec_version: $($json.spec_version)\" } else { Write-Output \"❌ spec_version: NOT FOUND\" }"

echo.

:: ============================================================
:: STEP 5: RETRIEVE SPEC
:: ============================================================
for /f "delims=" %%i in ('powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.spec_id) { Write-Output $json.spec_id }"') do set SPEC_ID=%%i

if not "!SPEC_ID!"=="" (
    echo ┌────────────────────────────────────────────────────────────┐
    echo │ STEP 5: Retrieve Generated Specification                  │
    echo └────────────────────────────────────────────────────────────┘
    echo.
    echo Endpoint: GET %BASE_URL%/api/v1/specs/!SPEC_ID!
    echo.

    curl -X GET "%BASE_URL%/api/v1/specs/!SPEC_ID!" ^
      -H "Authorization: Bearer !TOKEN!" ^
      -s -o spec_details.json -w "HTTP Status: %%{http_code}\n"

    echo.
    echo Response saved to: spec_details.json
    echo.
) else (
    echo ⚠️  Skipping spec retrieval (no spec_id found)
    echo.
)

:: ============================================================
:: STEP 6: SUMMARY
:: ============================================================
echo ┌────────────────────────────────────────────────────────────┐
echo │ STEP 6: Test Summary                                      │
echo └────────────────────────────────────────────────────────────┘
echo.

echo 📁 Files Created:
if exist register_response.json echo   ✅ register_response.json
if exist login_response.json echo   ✅ login_response.json
if exist generate_response.json echo   ✅ generate_response.json
if exist spec_details.json echo   ✅ spec_details.json
echo.

echo 🔍 Verification Checklist:
powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.spec_id) { Write-Output \"   ✅ Spec ID generated\" } else { Write-Output \"   ❌ Spec ID missing\" }"
powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.spec_json) { Write-Output \"   ✅ Spec JSON present\" } else { Write-Output \"   ❌ Spec JSON missing\" }"
powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.preview_url) { Write-Output \"   ✅ Preview URL generated\" } else { Write-Output \"   ❌ Preview URL missing\" }"
powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.estimated_cost -gt 0) { Write-Output \"   ✅ Cost calculated\" } else { Write-Output \"   ❌ Cost not calculated\" }"
powershell -Command "$json = Get-Content generate_response.json -Raw | ConvertFrom-Json; if ($json.compliance_check_id) { Write-Output \"   ✅ Compliance check queued\" } else { Write-Output \"   ❌ Compliance check not queued\" }"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    🎉 TEST COMPLETED                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

pause
endlocal
