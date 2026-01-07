@echo off
echo ================================================================================
echo Step 1: Authentication
echo ================================================================================

curl -X POST "http://localhost:8000/api/v1/auth/login" ^
-H "Content-Type: application/json" ^
-d "{\"username\":\"admin\",\"password\":\"bhiv2024\"}" ^
-o token_response.json

echo.
echo [+] Token saved to token_response.json
type token_response.json
echo.

echo ================================================================================
echo Step 2: Extract Token and Test GET /api/v1/reports/{spec_id}
echo ================================================================================

REM Extract token using PowerShell
for /f "delims=" %%i in ('powershell -Command "(Get-Content token_response.json | ConvertFrom-Json).access_token"') do set TOKEN=%%i

echo [+] Using token: %TOKEN%
echo.

curl -X GET "http://localhost:8000/api/v1/reports/spec_015ba76e" ^
-H "Authorization: Bearer %TOKEN%" ^
-H "Content-Type: application/json" ^
-o report_response.json

echo.
echo [+] Report response saved to report_response.json
type report_response.json
echo.

echo ================================================================================
echo Step 3: Verify Database Storage
echo ================================================================================

python -c "from app.database import engine; from sqlalchemy import text; conn = engine.connect(); spec = conn.execute(text('SELECT id, version, created_at FROM specs WHERE id = :spec_id'), {'spec_id': 'spec_015ba76e'}).fetchone(); print(f'[+] Spec: {spec}' if spec else '[!] Not found'); iters = conn.execute(text('SELECT COUNT(*) FROM iterations WHERE spec_id = :spec_id'), {'spec_id': 'spec_015ba76e'}).fetchone()[0]; print(f'[+] Iterations: {iters}'); evals = conn.execute(text('SELECT COUNT(*) FROM evaluations WHERE spec_id = :spec_id'), {'spec_id': 'spec_015ba76e'}).fetchone()[0]; print(f'[+] Evaluations: {evals}')"

echo.
echo ================================================================================
echo Step 4: Check Local Storage
echo ================================================================================

if exist "data\reports" (
    echo [*] data\reports:
    dir /b data\reports\*spec_015ba76e* 2>nul || echo    [!] No files found
) else (
    echo [!] data\reports not found
)

echo.
if exist "data\previews" (
    echo [*] data\previews:
    dir /b data\previews\*spec_015ba76e* 2>nul || echo    [!] No files found
) else (
    echo [!] data\previews not found
)

echo.
if exist "data\geometry_outputs" (
    echo [*] data\geometry_outputs:
    dir /b data\geometry_outputs\*spec_015ba76e* 2>nul || echo    [!] No files found
) else (
    echo [!] data\geometry_outputs not found
)

echo.
echo ================================================================================
echo Test Complete
echo ================================================================================

del token_response.json 2>nul
del report_response.json 2>nul
