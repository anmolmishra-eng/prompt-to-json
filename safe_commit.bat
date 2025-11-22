@echo off
echo 🚀 Safe commit script - Testing before push...

cd backend

echo.
echo 🔧 Testing dependencies...
python test_dependencies.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Dependency tests failed! Fix issues before committing.
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies OK! Proceeding with commit...

cd ..

echo.
echo 📝 Adding files to git...
git add .

echo.
set /p commit_msg="Enter commit message: "
git commit -m "%commit_msg%"

echo.
echo 🚀 Pushing to GitHub...
git push origin main

echo.
echo ✅ Successfully committed and pushed!
pause
