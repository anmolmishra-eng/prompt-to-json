@echo off
echo Pushing Backend folder to GitHub repository...

:: Initialize git if not already done
git init

:: Add remote origin if not exists
git remote add origin https://github.com/anmolmishra-eng/prompt-to-json.git 2>nul

:: Add all files
git add .

:: Commit all changes
git commit -m "Add complete FastAPI backend with comprehensive API documentation and setup instructions"

:: Push to GitHub (without force)
git push -u origin main

echo.
echo Backend folder has been pushed to GitHub successfully!
pause
