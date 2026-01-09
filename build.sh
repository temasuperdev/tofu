#!/bin/bash
# Build and push Docker image locally

set -e

REGISTRY="${REGISTRY:-ghcr.io}"
IMAGE_NAME="${IMAGE_NAME:-yourname/tofu}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
DOCKERFILE="${DOCKERFILE:-./docker/Dockerfile}"

IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
IMAGE_LATEST="${REGISTRY}/${IMAGE_NAME}:latest"

echo "Building Docker image: $IMAGE"
docker build -f $DOCKERFILE -t $IMAGE -t $IMAGE_LATEST .

echo "Successfully built: $IMAGE"
echo ""
echo "To push image to registry:"
echo "  docker push $IMAGE"
echo "  docker push $IMAGE_LATEST"
