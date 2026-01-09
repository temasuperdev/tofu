#!/bin/bash
# Обновленный скрипт build для работы с локальным registry

set -e

# Configuration
REGISTRY_HOST="${REGISTRY_HOST:-localhost:5000}"
IMAGE_NAME="${IMAGE_NAME:-demo-app}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
DOCKERFILE="${DOCKERFILE:-./docker/Dockerfile}"

IMAGE="${REGISTRY_HOST}/${IMAGE_NAME}:${IMAGE_TAG}"
IMAGE_LATEST="${REGISTRY_HOST}/${IMAGE_NAME}:latest"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Building Docker image for local registry...${NC}"
echo "Registry: $REGISTRY_HOST"
echo "Image: $IMAGE"
echo ""

# Build image
docker build -f $DOCKERFILE -t $IMAGE -t $IMAGE_LATEST .

echo ""
echo -e "${GREEN}✓ Build complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Start local registry:    bash registry.sh start"
echo "2. Push image:              docker push $IMAGE"
echo "3. Deploy to K3s:           bash deploy-local.sh"
