# Makefile для удобства

.PHONY: help install test build deploy clean logs logs-follow port-forward health-check swagger

IMAGE_REGISTRY ?= ghcr.io
IMAGE_NAME ?= yourname/tofu
IMAGE_TAG ?= latest
NAMESPACE ?= demo-app

help:
	@echo "Available commands:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make build         - Build Docker image"
	@echo "  make deploy        - Deploy to K3s"
	@echo "  make deploy-redis - Deploy Redis to K3s"
	@echo "  make clean         - Clean up pods and deployment"
	@echo "  make logs          - Show application logs"
	@echo "  make logs-follow   - Follow application logs"
	@echo "  make port-forward  - Port forward to application"
	@echo "  make health-check  - Check application health"
	@echo "  make verify        - Verify deployment"
	@echo "  make swagger       - Start Swagger UI"

install:
	pip install -r requirements.txt
	pip install pytest pytest-cov flasgger

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-fail-under=80
	@echo "Coverage report generated in htmlcov/"

build:
	docker build -f docker/Dockerfile -t ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .

deploy:
	@echo "Deploying to K3s..."
	sed -e "s|IMAGE_REGISTRY|${IMAGE_REGISTRY}|g" \
	    -e "s|IMAGE_NAME|${IMAGE_NAME}|g" \
	    -e "s|IMAGE_TAG|${IMAGE_TAG}|g" \
	    k8s/deployment.yaml | kubectl apply -f -
	kubectl apply -f k8s/ingress.yaml
	kubectl rollout status deployment/demo-app -n ${NAMESPACE} --timeout=5m

deploy-redis:
	@echo "Deploying Redis to K3s..."
	kubectl apply -f k8s/deployment.yaml
	kubectl rollout status deployment/demo-redis -n ${NAMESPACE} --timeout=5m

clean:
	kubectl delete namespace ${NAMESPACE} --ignore-not-found

logs:
	kubectl logs -l app=demo-app -n ${NAMESPACE} --tail=100

logs-follow:
	kubectl logs -f deployment/demo-app -n ${NAMESPACE}

port-forward:
	kubectl port-forward svc/demo-app 8080:80 -n ${NAMESPACE}

health-check:
	kubectl run health-check --image=curlimages/curl:latest --restart=Never --rm -i \
		-- curl http://demo-app.${NAMESPACE}.svc.cluster.local/api/health

verify:
	@echo "=== Deployment Status ==="
	kubectl get deployment -n ${NAMESPACE}
	@echo "\n=== Pod Status ==="
	kubectl get pods -n ${NAMESPACE}
	@echo "\n=== Service Status ==="
	kubectl get svc -n ${NAMESPACE}

swagger:
	python -c "from src.app import app; app.run(debug=True, host='0.0.0.0', port=5000)"