#!/bin/bash
# Скрипт для очистки всех Kubernetes ресурсов из YAML файлов
# Использует --ignore-not-found для предотвращения ошибок при отсутствующих ресурсах

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
echo -e "${BLUE}        🧹 CLEANUP - ALL KUBERNETES RESOURCES                ${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Configuration
NAMESPACE="demo-app"
K8S_DIR="k8s"

# Change to backend directory if script is run from root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

# Step 1: Delete all resources from YAML files (with ignore-not-found)
print_info "Deleting resources from Kubernetes manifests..."
print_warning "Note: NotFound errors are expected and will be ignored\n"

YAML_FILES=(
    "deployment-simple.yaml"
    "deployment-working.yaml"
    "deployment.yaml"
    "deployment-production.yaml"
    "ingress.yaml"
    "ingressroute.yaml"
    "letsencrypt-issuer.yaml"
    "networkpolicy.yaml"
    "redis.yaml"
)

DELETED_COUNT=0
NOT_FOUND_COUNT=0

for yaml_file in "${YAML_FILES[@]}"; do
    if [ -f "$K8S_DIR/$yaml_file" ]; then
        print_info "Deleting resources from $yaml_file..."
        if kubectl delete -f "$K8S_DIR/$yaml_file" --ignore-not-found=true 2>&1 | grep -q "not found"; then
            NOT_FOUND_COUNT=$((NOT_FOUND_COUNT + 1))
        else
            DELETED_COUNT=$((DELETED_COUNT + 1))
        fi
    else
        print_warning "File $K8S_DIR/$yaml_file not found, skipping..."
    fi
done

echo ""
print_info "Cleanup summary:"
echo "  - Files processed: ${#YAML_FILES[@]}"
echo "  - Resources deleted: $DELETED_COUNT"
echo "  - Resources not found (expected): $NOT_FOUND_COUNT"

# Step 2: Delete namespace if it exists
print_info "\nChecking namespace $NAMESPACE..."
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    print_info "Deleting namespace $NAMESPACE..."
    kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
    print_success "Namespace $NAMESPACE deleted"
else
    print_warning "Namespace $NAMESPACE not found, skipping..."
fi

# Step 3: Final check
print_info "\nChecking remaining resources..."
if kubectl get all -n "$NAMESPACE" 2>/dev/null | grep -q "demo-app"; then
    print_warning "Some resources might still exist in namespace $NAMESPACE"
    kubectl get all -n "$NAMESPACE" 2>/dev/null || true
else
    print_success "All resources cleaned up successfully!"
fi

echo ""
print_success "Cleanup complete!"
echo "All Kubernetes resources have been removed (if they existed)."
echo "NotFound errors during cleanup are normal and expected."
