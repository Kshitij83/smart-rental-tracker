@echo off
REM Smart Rental Tracker - Render Deployment Script (Windows)
echo 🚀 Smart Rental Tracker - Render Deployment Script
echo ==================================================

REM Check if git is available
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed. Please install Git first.
    pause
    exit /b 1
)

REM Check if we're in a git repository
if not exist ".git" (
    echo ❌ Not in a git repository. Please initialize git first.
    pause
    exit /b 1
)

REM Check for uncommitted changes
git diff --quiet
if %errorlevel% neq 0 (
    echo ⚠️  You have uncommitted changes. Please commit them first:
    git status --short
    echo.
    set /p commit_changes="Do you want to commit all changes now? (y/n): "
    if /i "%commit_changes%"=="y" (
        git add .
        git commit -m "Prepare for Render deployment - %date% %time%"
    ) else (
        echo ❌ Please commit your changes and run this script again.
        pause
        exit /b 1
    )
)

REM Push to remote repository
echo 📤 Pushing changes to remote repository...
git push origin main

if %errorlevel% equ 0 (
    echo ✅ Code pushed successfully!
    echo.
    echo 🎯 Next steps:
    echo 1. Go to https://dashboard.render.com
    echo 2. Click 'New +' → 'Blueprint'
    echo 3. Connect your GitHub repository
    echo 4. Render will automatically detect the render.yaml file
    echo 5. Click 'Apply' to deploy both services
    echo.
    echo 📚 For detailed instructions, see RENDER_DEPLOYMENT_GUIDE.md
    echo.
    echo 🌐 Your application will be available at:
    echo    Frontend: https://smart-rental-tracker-frontend.onrender.com
    echo    Backend:  https://smart-rental-tracker-backend.onrender.com
) else (
    echo ❌ Failed to push changes. Please check your git configuration.
    pause
    exit /b 1
)

pause
