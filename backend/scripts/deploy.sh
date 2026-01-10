# K3s Deploy Helper Script
#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="demo-app"
DEPLOYMENT="demo-app"
REGISTRY="${REGISTRY:-ghcr.io}"
IMAGE_NAME="${IMAGE_NAME:-yourname/tofu}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo -e "${BLUE}=== K3s Application Deployment Script ===${NC}\n"

# Function to print colored output
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
    print_error "Failed to connect to K3s cluster"
    exit 1
fi

# Create namespace
print_info "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f - > /dev/null
print_success "Namespace created/updated"

# Apply deployment manifest
print_info "Applying Kubernetes deployment manifests..."
sed -e "s|IMAGE_REGISTRY|$REGISTRY|g" \
    -e "s|IMAGE_NAME|$IMAGE_NAME|g" \
    -e "s|IMAGE_TAG|$IMAGE_TAG|g" \
    k8s/deployment-production.yaml | kubectl apply -f - > /dev/null
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
fi

# Display deployment status
echo -e "\n${BLUE}=== Deployment Status ===${NC}"
echo -e "\n${YELLOW}Deployments:${NC}"
kubectl get deployment -n $NAMESPACE

echo -e "\n${YELLOW}Pods:${NC}"
kubectl get pods -n $NAMESPACE

echo -e "\n${YELLOW}Services:${NC}"
kubectl get svc -n $NAMESPACE

echo -e "\n${YELLOW}Ingresses:${NC}"
kubectl get ingress -n $NAMESPACE

# Port forward info
echo -e "\n${BLUE}=== Access Application ===${NC}"
print_info "To access the application locally, run:"
echo "  kubectl port-forward svc/$DEPLOYMENT 8080:80 -n $NAMESPACE"
echo ""
echo "Then open: http://localhost:8080"
echo ""

# Health check
print_info "Performing health check..."
SERVICE_IP=$(kubectl get svc $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")

if [ -z "$SERVICE_IP" ]; then
    print_warning "Could not get service IP"
else
    print_info "Service IP: $SERVICE_IP"
    
    # Create a temporary pod for health check
    print_info "Running health check (this may take a moment)..."
    if kubectl run health-check --image=curlimages/curl:latest --restart=Never --rm -i \
        --overrides='{"spec":{"serviceAccountName":"'$DEPLOYMENT'"}}' \
        -- curl -s http://$DEPLOYMENT.$NAMESPACE.svc.cluster.local/api/health > /dev/null 2>&1; then
        print_success "Application health check passed"
    else
        print_warning "Could not perform health check from cluster"
    fi
fi

print_success "Deployment completed successfully!"
