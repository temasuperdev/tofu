#!/bin/bash
# Makefile альтернатива для локального развития

set -e

NAMESPACE="demo-app"
REGISTRY_HOST="localhost:5000"
IMAGE_NAME="demo-app"
IMAGE_TAG="latest"

case "${1:-help}" in
    help)
        echo "Local Development Commands"
        echo ""
        echo "Registry:"
        echo "  make-local registry-start      - Start local Docker registry"
        echo "  make-local registry-status     - Check registry status"
        echo "  make-local registry-stop       - Stop registry"
        echo "  make-local registry-logs       - View registry logs"
        echo ""
        echo "Build & Deploy:"
        echo "  make-local setup               - Full setup (registry + build + deploy)"
        echo "  make-local build               - Build Docker image"
        echo "  make-local push                - Push to local registry"
        echo "  make-local deploy              - Deploy to K3s"
        echo ""
        echo "Development:"
        echo "  make-local port-forward        - Port forward (8080:80)"
        echo "  make-local logs                - View application logs"
        echo "  make-local test                - Run tests"
        echo ""
        echo "Cleanup:"
        echo "  make-local clean               - Remove all K3s resources"
        echo "  make-local clean-registry      - Remove registry"
        echo "  make-local clean-all           - Full cleanup"
        ;;
        
    registry-start)
        bash registry.sh start
        ;;
        
    registry-stop)
        bash registry.sh stop
        ;;
        
    registry-status)
        bash registry.sh status
        ;;
        
    registry-logs)
        bash registry.sh logs
        ;;
        
    setup)
        bash setup-local.sh
        ;;
        
    build)
        REGISTRY_HOST=$REGISTRY_HOST IMAGE_NAME=$IMAGE_NAME IMAGE_TAG=$IMAGE_TAG bash build-local.sh
        ;;
        
    push)
        echo "Pushing $REGISTRY_HOST/$IMAGE_NAME:$IMAGE_TAG to registry..."
        docker push "$REGISTRY_HOST/$IMAGE_NAME:$IMAGE_TAG"
        docker push "$REGISTRY_HOST/$IMAGE_NAME:latest"
        echo "✓ Push complete"
        ;;
        
    deploy)
        REGISTRY_HOST=$REGISTRY_HOST IMAGE_NAME=$IMAGE_NAME IMAGE_TAG=$IMAGE_TAG bash deploy-local.sh
        ;;
        
    port-forward)
        echo "Port forwarding to application..."
        echo "App URL: http://localhost:8080"
        echo ""
        kubectl port-forward svc/$IMAGE_NAME 8080:80 -n $NAMESPACE
        ;;
        
    logs)
        kubectl logs -f deployment/$IMAGE_NAME -n $NAMESPACE
        ;;
        
    test)
        pytest tests/ -v --cov=src
        ;;
        
    clean)
        kubectl delete namespace $NAMESPACE --ignore-not-found=true
        echo "✓ K3s resources cleaned"
        ;;
        
    clean-registry)
        bash registry.sh clean
        ;;
        
    clean-all)
        bash cleanup-local.sh
        ;;
        
    *)
        echo "Unknown command: $1"
        echo "Run 'make-local help' for available commands"
        exit 1
        ;;
esac
