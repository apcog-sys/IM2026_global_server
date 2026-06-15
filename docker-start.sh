#!/bin/bash

# Docker Quick Start Script for Global Server (GS1)

set -e

echo "======================================"
echo "Global Server Docker Setup"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Check if images need to be built
echo "Building Docker images..."
docker-compose build

echo ""
echo "======================================"
echo "Starting services..."
echo "======================================"
echo ""

# Start services
docker-compose up -d

echo ""
echo "======================================"
echo "Services Started!"
echo "======================================"
echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check health
echo ""
echo "Checking service health..."
echo ""

# Test MySQL
echo -n "MySQL: "
if docker exec gs1_mysql mysqladmin ping -u root -proot &> /dev/null; then
    echo "✓ Running"
else
    echo "⚠ Starting up..."
fi

# Test Application
echo -n "Application (GS1): "
if curl -s http://localhost:9000/health > /dev/null; then
    echo "✓ Running"
else
    echo "⚠ Starting up..."
fi

echo ""
echo "======================================"
echo "Docker containers are running!"
echo "======================================"
echo ""
echo "📊 Access Points:"
echo "  - Web UI (GS1): http://localhost:9000"
echo "  - API (GS1): http://localhost:9000/api"
echo "  - CA Service: http://localhost:9002"
echo "  - CA API: http://localhost:9002/api"
echo "  - Database: localhost:3306"
echo ""
echo "📝 Database Credentials:"
echo "  - Username: root"
echo "  - Password: root"
echo "  - Database: gs1"
echo ""
echo "🛠️ Useful Commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - GS1 logs: docker-compose logs -f gs1_app"
echo "  - CA logs: docker-compose logs -f ca_service"
echo "  - Stop: docker-compose stop"
echo "  - Restart: docker-compose restart"
echo "  - Down: docker-compose down"
echo ""
echo "📖 Documentation: See DOCKER_SETUP.md and CA_management/DOCKER_README.md"
echo ""

