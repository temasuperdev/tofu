#!/bin/bash
# Обновленный скрипт deploy для работы с локальным K3s и registry

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
REGISTRY_HOST="${REGISTRY_HOST:-localhost:5000}"
IMAGE_NAME="${IMAGE_NAME:-demo-app}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

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
echo -e "${BLUE}       🚀 LOCAL K3s DEPLOYMENT (Local Registry)              ${NC}"
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
print_success "Namespace ready"

# Update K8s manifest for local registry
print_info "Generating Kubernetes manifest with local registry..."
sed -e "s|IMAGE_REGISTRY|${REGISTRY_HOST}|g" \
    -e "s|IMAGE_NAME|${IMAGE_NAME}|g" \
    -e "s|IMAGE_TAG|${IMAGE_TAG}|g" \
    k8s/deployment.yaml | kubectl apply -f - > /dev/null
print_success "Deployment manifest applied"

# Apply ingress manifest
print_info "Applying ingress configuration..."
kubectl apply -f k8s/ingress.yaml > /dev/null
print_success "Ingress configuration applied"

# Wait for rollout
print_info "Waiting for deployment to rollout (timeout: 5m)..."
if kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE --timeout=5m > /dev/null 2>&1; then
    print_success "Deployment rollout completed successfully"
else
    print_warning "Deployment rollout timed out or failed"
    print_info "Checking pod status..."
    kubectl get pods -n $NAMESPACE
fi

# Display deployment status
echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                  📊 DEPLOYMENT STATUS${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Deployments:${NC}"
kubectl get deployment -n $NAMESPACE

echo -e "\n${YELLOW}Pods:${NC}"
kubectl get pods -n $NAMESPACE

echo -e "\n${YELLOW}Services:${NC}"
kubectl get svc -n $NAMESPACE

echo -e "\n${YELLOW}Ingresses:${NC}"
kubectl get ingress -n $NAMESPACE

# Port forward info
echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                   🌐 ACCESS APPLICATION${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

print_info "To access the application locally, run:"
echo -e "${GREEN}  kubectl port-forward svc/$DEPLOYMENT 8080:80 -n $NAMESPACE${NC}"
echo ""
echo "Then open in browser: http://localhost:8080"
echo ""

# Health check
print_info "Performing health check..."
SERVICE_IP=$(kubectl get svc $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")

if [ -z "$SERVICE_IP" ]; then
    print_warning "Could not get service IP, skipping health check"
else
    print_info "Service IP: $SERVICE_IP"
    
    # Try to check health
    if kubectl run health-check --image=curlimages/curl:latest --restart=Never --rm -i \
        -- curl -s http://$DEPLOYMENT.$NAMESPACE.svc.cluster.local/api/health > /dev/null 2>&1; then
        print_success "Application health check passed"
    else
        print_warning "Health check could not be performed"
    fi
fi

print_success "Local K3s deployment completed!"
echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}\n"
