@echo off
echo ========================================
echo   MESHY AI INTEGRATION - QUICK TEST
echo ========================================
echo.

echo [1/3] Verifying configuration...
python verify_meshy_config.py
echo.

echo [2/3] Testing Meshy AI directly...
echo (This will take 1-2 minutes)
python test_meshy_integration.py
echo.

echo [3/3] Starting server for full test...
echo.
echo Server will start at http://localhost:8000
echo.
echo To test the generate endpoint, open another terminal and run:
echo.
echo curl -X POST http://localhost:8000/api/v1/generate ^
echo   -H "Content-Type: application/json" ^
echo   -d "{\"user_id\":\"test_user\",\"prompt\":\"Design a modern 3BHK apartment\",\"city\":\"Mumbai\"}"
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python -m uvicorn app.main:app --reload --port 8000
