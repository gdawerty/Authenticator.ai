#!/bin/bash

# Authenticator.AI Docker Setup Script
# This script helps you build and run the complete application stack

set -e  # Exit on any error

echo "🚀 Authenticator.AI Docker Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    print_success "Docker Compose is available"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p backend/uploads
    mkdir -p backend/tmp_uploads
    mkdir -p backend/logs
    mkdir -p data
    
    print_success "Directories created"
}

# Build and start services
build_and_start() {
    print_status "Building and starting services..."
    
    # Use docker-compose if available, otherwise use docker compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    print_status "Pulling SQL Server image..."
    docker pull mcr.microsoft.com/mssql/server:2019-latest
    
    print_status "Building application containers..."
    $COMPOSE_CMD build --no-cache
    
    print_status "Starting services..."
    $COMPOSE_CMD up -d
    
    print_success "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for SQL Server
    print_status "Waiting for SQL Server to start..."
    sleep 30
    
    # Wait for backend
    print_status "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -f http://localhost:8001/health &> /dev/null; then
            break
        fi
        sleep 5
        echo -n "."
    done
    echo
    
    # Wait for frontend
    print_status "Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -f http://localhost:5174 &> /dev/null; then
            break
        fi
        sleep 5
        echo -n "."
    done
    echo
    
    print_success "All services are ready!"
}

# Display service information
show_services() {
    echo
    echo "🎉 Authenticator.AI is now running!"
    echo "=================================="
    echo
    echo "📊 Service URLs:"
    echo "  Frontend:  http://localhost:5174"
    echo "  Backend:   http://localhost:8001"
    echo "  API Docs:  http://localhost:8001/docs"
    echo
    echo "🗄️  Database:"
    echo "  SQL Server: localhost:1433"
    echo "  Username:   sa"
    echo "  Password:   SecurePassword123!"
    echo
    echo "📋 Useful Commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop all:     docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo "  Rebuild:      docker-compose up --build"
    echo
}

# Main execution
main() {
    check_docker
    check_docker_compose
    create_directories
    build_and_start
    wait_for_services
    show_services
}

# Handle different command line arguments
case "${1:-}" in
    "start"|"up")
        print_status "Starting existing containers..."
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d
        else
            docker compose up -d
        fi
        ;;
    "stop"|"down")
        print_status "Stopping containers..."
        if command -v docker-compose &> /dev/null; then
            docker-compose down
        else
            docker compose down
        fi
        ;;
    "restart")
        print_status "Restarting containers..."
        if command -v docker-compose &> /dev/null; then
            docker-compose restart
        else
            docker compose restart
        fi
        ;;
    "logs")
        if command -v docker-compose &> /dev/null; then
            docker-compose logs -f
        else
            docker compose logs -f
        fi
        ;;
    "clean")
        print_warning "This will remove all containers, images, and volumes!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v docker-compose &> /dev/null; then
                docker-compose down -v --rmi all
            else
                docker compose down -v --rmi all
            fi
            print_success "Cleanup completed"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Authenticator.AI Docker Setup Script"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  (no command)  Full setup and start"
        echo "  start|up      Start existing containers"
        echo "  stop|down     Stop containers"
        echo "  restart       Restart containers"
        echo "  logs          View container logs"
        echo "  clean         Remove all containers and data"
        echo "  help          Show this help message"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
