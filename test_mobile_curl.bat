@echo off
echo ============================================================
echo Testing Mobile Generate Endpoint with CURL
echo ============================================================
echo.

echo [1/3] Authenticating...
curl -X POST "http://localhost:8000/api/v1/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=admin&password=bhiv2024" ^
  -o auth_response.json -s

echo [OK] Authentication complete
echo.

echo [2/3] Extracting token...
for /f "tokens=2 delims=:," %%a in ('type auth_response.json ^| findstr "access_token"') do set TOKEN=%%a
set TOKEN=%TOKEN:"=%
set TOKEN=%TOKEN: =%
echo [OK] Token extracted
echo.

echo [3/3] Testing mobile generate endpoint...
curl -X POST "http://localhost:8000/api/v1/mobile/generate" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"mobile_test_user\",\"prompt\":\"Create a modern living room with minimalist furniture\",\"project_id\":\"proj_mobile_001\",\"context\":{\"device\":\"android\"}}" ^
  -o mobile_response.json -w "\nStatus: %%{http_code}\n"

echo.
echo [RESULT] Response saved to mobile_response.json
type mobile_response.json
echo.

echo ============================================================
echo Verifying Database Storage
echo ============================================================
echo.

for /f "tokens=2 delims=:," %%a in ('type mobile_response.json ^| findstr "spec_id"') do set SPEC_ID=%%a
set SPEC_ID=%SPEC_ID:"=%
set SPEC_ID=%SPEC_ID: =%

if not "%SPEC_ID%"=="" (
    echo [CHECK] Verifying spec_id: %SPEC_ID%
    curl -X GET "http://localhost:8000/api/v1/specs/%SPEC_ID%" ^
      -H "Authorization: Bearer %TOKEN%" ^
      -s -o db_verify.json -w "Status: %%{http_code}\n"
    echo [OK] Database verification complete
    type db_verify.json
) else (
    echo [SKIP] No spec_id found in response
)

echo.
echo ============================================================
echo Test Complete
echo ============================================================
