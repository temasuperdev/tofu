#!/bin/bash
# Развертывание в K3s без локального Docker Registry (использует встроенный containerd)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
NAMESPACE="demo-app"
DEPLOYMENT="demo-app"

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       🚀 K3s DIRECT DEPLOYMENT (Builtin Images)             ${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    exit 1
fi

# Check cluster connectivity
print_info "Checking K3s cluster connectivity..."
if kubectl cluster-info &> /dev/null; then
    print_success "Connected to K3s cluster"
else
    print_error "Failed to connect to K3s cluster. Is K3s running?"
    exit 1
fi

# Create namespace
print_info "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f - > /dev/null
print_success "Namespace created"

# Apply deployment directly using ghcr.io images (or local if available)
print_info "Applying Kubernetes manifests..."
kubectl apply -f k8s/deployment.yaml -n $NAMESPACE
kubectl apply -f k8s/ingress.yaml -n $NAMESPACE
print_success "Manifests applied"

# Wait for deployment
print_info "Waiting for deployment to be ready (timeout: 5 minutes)..."
if kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE --timeout=5m 2>/dev/null; then
    print_success "Deployment is ready!"
else
    print_error "Deployment failed or timed out"
    echo ""
    echo "Debug info:"
    kubectl describe deployment $DEPLOYMENT -n $NAMESPACE
    kubectl describe pods -n $NAMESPACE
    exit 1
fi

# Get pod information
print_info "Pod status:"
kubectl get pods -n $NAMESPACE

# Port forwarding info
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}📌 TO ACCESS THE APP, RUN IN ANOTHER TERMINAL:${NC}"
echo -e "${BLUE}   kubectl port-forward svc/$DEPLOYMENT 8080:80 -n $NAMESPACE${NC}"
echo ""
echo -e "${YELLOW}Then open:${NC}"
echo -e "${BLUE}   http://localhost:8080${NC}"
echo ""

echo -e "${YELLOW}📌 TO VIEW LOGS:${NC}"
echo -e "${BLUE}   kubectl logs -f deployment/$DEPLOYMENT -n $NAMESPACE${NC}"
echo ""

echo -e "${YELLOW}📌 TO TROUBLESHOOT:${NC}"
echo -e "${BLUE}   kubectl describe pod -n $NAMESPACE${NC}"
echo -e "${BLUE}   kubectl get events -n $NAMESPACE${NC}"
echo ""

print_success "Setup complete!"
