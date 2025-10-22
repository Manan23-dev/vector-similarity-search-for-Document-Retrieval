#!/bin/bash

# Docker build and deployment script for RAG System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 RAG System Docker Deployment Script${NC}"
echo "================================================"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose not found. Using docker compose instead."
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Build the Docker image
print_status "Building RAG System Docker image..."
docker build -t rag-system:latest .

if [ $? -eq 0 ]; then
    print_status "✅ Docker image built successfully!"
else
    print_error "❌ Docker build failed!"
    exit 1
fi

# Run the container
print_status "Starting RAG System container..."
docker run -d \
    --name rag-system \
    --restart unless-stopped \
    -p 8000:8000 \
    -e PYTHONUNBUFFERED=1 \
    rag-system:latest

if [ $? -eq 0 ]; then
    print_status "✅ Container started successfully!"
    print_status "🌐 RAG System is now running at: http://localhost:8000"
    print_status "📚 API Documentation: http://localhost:8000/docs"
    print_status "❤️  Health Check: http://localhost:8000/health"
else
    print_error "❌ Failed to start container!"
    exit 1
fi

# Show container status
print_status "Container Status:"
docker ps | grep rag-system

echo ""
echo -e "${GREEN}🎉 RAG System is now running!${NC}"
echo "================================================"
echo "To stop the container: docker stop rag-system"
echo "To remove the container: docker rm rag-system"
echo "To view logs: docker logs rag-system"
echo "To restart: docker restart rag-system"
echo "================================================"
