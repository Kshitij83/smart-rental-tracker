#!/bin/bash

# Smart Rental Tracker - Render Deployment Script
echo "🚀 Smart Rental Tracker - Render Deployment Script"
echo "=================================================="

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please initialize git first."
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes. Please commit them first:"
    git status --short
    echo ""
    read -p "Do you want to commit all changes now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Prepare for Render deployment - $(date)"
    else
        echo "❌ Please commit your changes and run this script again."
        exit 1
    fi
fi

# Push to remote repository
echo "📤 Pushing changes to remote repository..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Code pushed successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Go to https://dashboard.render.com"
    echo "2. Click 'New +' → 'Blueprint'"
    echo "3. Connect your GitHub repository"
    echo "4. Render will automatically detect the render.yaml file"
    echo "5. Click 'Apply' to deploy both services"
    echo ""
    echo "📚 For detailed instructions, see RENDER_DEPLOYMENT_GUIDE.md"
    echo ""
    echo "🌐 Your application will be available at:"
    echo "   Frontend: https://smart-rental-tracker-frontend.onrender.com"
    echo "   Backend:  https://smart-rental-tracker-backend.onrender.com"
else
    echo "❌ Failed to push changes. Please check your git configuration."
    exit 1
fi
