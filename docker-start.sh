#!/bin/bash

# Docker Start Script
# This script helps you start the AI Agents application with Docker

echo "==================================="
echo "  AI Agents - Docker Startup"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker is installed"
echo "✓ Docker Compose is installed"
echo ""

# Check if .env.local file exists
if [ ! -f .env.local ]; then
    echo "⚠️  No .env.local file found"
    echo "Creating .env.local from env.example..."
    cp env.example .env.local
    echo ""
    echo "❗ IMPORTANT: Please edit .env.local and add your OpenAI API key"
    echo "   File location: .env.local"
    echo ""
    read -p "Press Enter after you've updated the .env.local file..."
fi

# Check if OPENAI_API_KEY is set
source .env.local
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-api-key-here" ]; then
    echo "❌ Error: OPENAI_API_KEY is not set in .env.local file"
    echo "Please edit .env.local and add your actual OpenAI API key"
    exit 1
fi

echo "✓ Found .env.local with your API key"

echo "✓ Environment variables configured"
echo ""

# Ask user if they want to rebuild
read -p "Do you want to rebuild the images? (y/N): " rebuild
echo ""

if [ "$rebuild" = "y" ] || [ "$rebuild" = "Y" ]; then
    echo "🔨 Building Docker images..."
    docker-compose build --no-cache
    if [ $? -ne 0 ]; then
        echo "❌ Build failed"
        exit 1
    fi
    echo "✓ Build completed successfully"
    echo ""
fi

# Start the services
echo "🚀 Starting services..."
echo ""
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "  ✅ Application Started Successfully!"
    echo "==================================="
    echo ""
    echo "Frontend:  http://localhost:3000"
    echo "Backend:   http://localhost:8000"
    echo "API Docs:  http://localhost:8000/api/py/docs"
    echo ""
    echo "To view logs:       docker-compose logs -f"
    echo "To stop services:   docker-compose down"
    echo ""
else
    echo ""
    echo "❌ Failed to start services"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

