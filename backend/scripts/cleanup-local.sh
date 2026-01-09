#!/bin/bash
# Cleanup скрипт для удаления локальной настройки

set -e

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}               🧹 CLEANUP - LOCAL SETUP                      ${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Configuration
NAMESPACE="demo-app"
REGISTRY_CONTAINER="local-docker-registry"

# Step 1: Remove K3s deployment
print_info "Removing K3s deployment..."
if kubectl get namespace $NAMESPACE &> /dev/null; then
    kubectl delete namespace $NAMESPACE
    print_success "K3s namespace removed"
else
    print_warning "K3s namespace not found"
fi

# Step 2: Stop and remove registry
print_info "Cleaning up Docker registry..."
if bash registry.sh clean 2>/dev/null; then
    print_success "Registry cleaned up"
else
    print_warning "Could not clean up registry (might already be stopped)"
fi

# Step 3: Remove local Docker images
print_info "Removing local Docker images..."
if docker images | grep -q "localhost:5000/demo-app"; then
    docker rmi -f localhost:5000/demo-app:latest localhost:5000/demo-app:* 2>/dev/null || true
    print_success "Local images removed"
else
    print_warning "No local images found"
fi

print_success "Cleanup complete!"
echo ""
echo -e "${BLUE}All local resources have been removed.${NC}"
echo "To start again, run: ${GREEN}bash setup-local.sh${NC}"
echo ""
