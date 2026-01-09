#!/bin/bash
# Скрипт для запуска локального Docker Registry

set -e

REGISTRY_PORT=5000
REGISTRY_CONTAINER_NAME="local-docker-registry"
REGISTRY_IMAGE="registry:2"
REGISTRY_DATA_VOLUME="registry-data"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}     🐳 LOCAL DOCKER REGISTRY (localhost:${REGISTRY_PORT})     ${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Check if Docker is running
if ! docker ps &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Parse arguments
case "${1:-start}" in
    start)
        print_info "Starting local Docker Registry..."
        
        # Create volume if not exists
        if ! docker volume ls | grep -q "$REGISTRY_DATA_VOLUME"; then
            print_info "Creating Docker volume: $REGISTRY_DATA_VOLUME"
            docker volume create "$REGISTRY_DATA_VOLUME"
        fi
        
        # Check if container already running
        if docker ps | grep -q "$REGISTRY_CONTAINER_NAME"; then
            print_warning "Registry already running on port $REGISTRY_PORT"
            print_info "Registry URL: http://localhost:$REGISTRY_PORT"
            exit 0
        fi
        
        # Check if container exists but stopped
        if docker ps -a | grep -q "$REGISTRY_CONTAINER_NAME"; then
            print_info "Container exists, starting it..."
            docker start "$REGISTRY_CONTAINER_NAME"
        else
            # Create and run registry container
            print_info "Creating new registry container..."
            docker run -d \
                --name "$REGISTRY_CONTAINER_NAME" \
                -p "$REGISTRY_PORT:5000" \
                -v "$REGISTRY_DATA_VOLUME:/var/lib/registry" \
                -e REGISTRY_STORAGE_DELETE_ENABLED=true \
                "$REGISTRY_IMAGE"
        fi
        
        # Wait for registry to be ready
        print_info "Waiting for registry to be ready..."
        for i in {1..30}; do
            if curl -s http://localhost:$REGISTRY_PORT/v2/ > /dev/null 2>&1; then
                print_success "Registry is ready!"
                break
            fi
            if [ $i -eq 30 ]; then
                print_error "Registry failed to start"
                exit 1
            fi
            sleep 1
        done
        
        print_success "Local Docker Registry started successfully!"
        echo ""
        echo -e "${BLUE}Usage:${NC}"
        echo "  Tag image:   docker tag myapp:latest localhost:$REGISTRY_PORT/myapp:latest"
        echo "  Push image:  docker push localhost:$REGISTRY_PORT/myapp:latest"
        echo "  Pull image:  docker pull localhost:$REGISTRY_PORT/myapp:latest"
        echo ""
        echo -e "${BLUE}Registry info:${NC}"
        echo "  URL: http://localhost:$REGISTRY_PORT"
        echo "  API: http://localhost:$REGISTRY_PORT/v2/_catalog"
        echo ""
        echo -e "${BLUE}To view images:${NC}"
        echo "  curl http://localhost:$REGISTRY_PORT/v2/_catalog | jq ."
        echo ""
        ;;
        
    stop)
        print_info "Stopping Docker Registry..."
        if docker ps | grep -q "$REGISTRY_CONTAINER_NAME"; then
            docker stop "$REGISTRY_CONTAINER_NAME"
            print_success "Registry stopped"
        else
            print_warning "Registry is not running"
        fi
        ;;
        
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
        
    logs)
        if docker ps | grep -q "$REGISTRY_CONTAINER_NAME"; then
            docker logs -f "$REGISTRY_CONTAINER_NAME"
        else
            print_error "Registry is not running"
            exit 1
        fi
        ;;
        
    status)
        if docker ps | grep -q "$REGISTRY_CONTAINER_NAME"; then
            print_success "Registry is running on port $REGISTRY_PORT"
            echo ""
            print_info "Container info:"
            docker ps --filter "name=$REGISTRY_CONTAINER_NAME"
            echo ""
            print_info "Available images:"
            curl -s http://localhost:$REGISTRY_PORT/v2/_catalog | jq '.repositories[]' 2>/dev/null || echo "  (none)"
        else
            print_warning "Registry is not running"
        fi
        ;;
        
    clean)
        print_info "Cleaning up registry..."
        if docker ps -a | grep -q "$REGISTRY_CONTAINER_NAME"; then
            docker rm -f "$REGISTRY_CONTAINER_NAME"
            print_success "Container removed"
        fi
        if docker volume ls | grep -q "$REGISTRY_DATA_VOLUME"; then
            docker volume rm "$REGISTRY_DATA_VOLUME"
            print_success "Volume removed"
        fi
        print_success "Cleanup complete"
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|clean}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the local registry"
        echo "  stop    - Stop the registry"
        echo "  restart - Restart the registry"
        echo "  logs    - Show registry logs"
        echo "  status  - Show registry status"
        echo "  clean   - Remove registry container and data"
        exit 1
        ;;
esac
