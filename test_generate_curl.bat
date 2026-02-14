@echo off
echo ============================================================
echo Testing /api/v1/generate Endpoint with CURL
echo ============================================================

set BASE_URL=http://127.0.0.1:8000

echo.
echo 1. Registering admin user...
curl -X POST "%BASE_URL%/api/v1/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"admin\",\"full_name\":\"Admin User\"}"

echo.
echo.
echo 2. Logging in...
curl -X POST "%BASE_URL%/api/v1/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=admin&password=admin" ^
  -o auth_response.json

echo.
echo Login response saved to auth_response.json

echo.
echo 3. Extracting token...
for /f "tokens=2 delims=:," %%a in ('type auth_response.json ^| findstr "access_token"') do set TOKEN=%%a
set TOKEN=%TOKEN:"=%
set TOKEN=%TOKEN: =%
echo Token: %TOKEN:~0,20%...

echo.
echo 4. Testing generate endpoint...
curl -X POST "%BASE_URL%/api/v1/generate" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -d "{\"user_id\":\"admin\",\"prompt\":\"Design a 3-bedroom residential building in Mumbai with 2000 sq ft area\",\"project_id\":\"proj_001\",\"context\":{\"city\":\"Mumbai\",\"plot_area\":2000,\"building_type\":\"residential\"}}" ^
  -o generate_response.json

echo.
echo.
echo Response saved to generate_response.json
echo.
type generate_response.json

echo.
echo.
echo ============================================================
echo Test Complete
echo ============================================================
pause
