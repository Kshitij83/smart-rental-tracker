#!/bin/bash

# Production build script for Smart Rental Tracker Frontend
echo "🚀 Building Smart Rental Tracker Frontend for production..."

# Set production environment
export NODE_ENV=production
export NEXT_PUBLIC_API_URL=https://smart-rental-tracker-backend.onrender.com

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the application
echo "🔨 Building application..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo "📁 Static files are in the 'out' directory"
else
    echo "❌ Build failed!"
    exit 1
fi