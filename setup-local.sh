#!/bin/bash
# Полная локальная настройка: запускает registry и развертывает приложение

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
REGISTRY_HOST="localhost:5000"
IMAGE_NAME="demo-app"
IMAGE_TAG="latest"
NAMESPACE="demo-app"

echo -e "${GREEN}"
cat << "EOF"

╔════════════════════════════════════════════════════════════╗
║                                                            ║
║  🚀 LOCAL K3S + DOCKER REGISTRY SETUP                     ║
║                                                            ║
║  This script will:                                         ║
║  1. Start local Docker Registry (localhost:5000)          ║
║  2. Build Docker image                                    ║
║  3. Push to local registry                                ║
║  4. Deploy to K3s cluster                                 ║
║  5. Port forward for local access                         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

EOF
echo -e "${NC}"

# Step 1: Start Registry
print_step "1️⃣  STARTING LOCAL DOCKER REGISTRY"

if ! bash registry.sh status > /dev/null 2>&1; then
    print_info "Starting registry..."
    bash registry.sh start
    sleep 2
fi
print_success "Registry is running on http://localhost:5000"

# Step 2: Build image
print_step "2️⃣  BUILDING DOCKER IMAGE"

print_info "Building image: $REGISTRY_HOST/$IMAGE_NAME:$IMAGE_TAG"
REGISTRY_HOST=$REGISTRY_HOST IMAGE_NAME=$IMAGE_NAME IMAGE_TAG=$IMAGE_TAG bash build-local.sh

# Step 3: Push to registry
print_step "3️⃣  PUSHING IMAGE TO LOCAL REGISTRY"

print_info "Pushing image to local registry..."
docker push "$REGISTRY_HOST/$IMAGE_NAME:$IMAGE_TAG"
docker push "$REGISTRY_HOST/$IMAGE_NAME:latest"
print_success "Image pushed successfully!"

# Step 4: Deploy to K3s
print_step "4️⃣  DEPLOYING TO K3S CLUSTER"

print_info "Deploying application..."
REGISTRY_HOST=$REGISTRY_HOST IMAGE_NAME=$IMAGE_NAME IMAGE_TAG=$IMAGE_TAG bash deploy-local.sh

# Step 5: Setup port forward in background
print_step "5️⃣  SETTING UP LOCAL ACCESS"

print_info "Application is deployed and ready!"
echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. In a new terminal, run port-forward:"
echo -e "   ${GREEN}kubectl port-forward svc/$IMAGE_NAME 8080:80 -n $NAMESPACE${NC}"
echo ""
echo "2. Then open in browser:"
echo -e "   ${GREEN}http://localhost:8080${NC}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo ""
echo "  View logs:"
echo -e "    ${GREEN}kubectl logs -f deployment/$IMAGE_NAME -n $NAMESPACE${NC}"
echo ""
echo "  View pod status:"
echo -e "    ${GREEN}kubectl get pods -n $NAMESPACE${NC}"
echo ""
echo "  View local images in registry:"
echo -e "    ${GREEN}curl http://localhost:5000/v2/_catalog | jq .${NC}"
echo ""
echo "  Stop registry:"
echo -e "    ${GREEN}bash registry.sh stop${NC}"
echo ""
echo "  Remove all (cleanup):"
echo -e "    ${GREEN}bash cleanup-local.sh${NC}"
echo ""
