#!/bin/bash
# Agentic AI - Deployment Script
# Usage: ./deploy.sh [dev|staging|prod]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="agentic-ai"
IMAGE="idm.wezzel.com:5050/crab-meat-repos/agentic-ai"
TAG="${CI_COMMIT_SHA:-latest}"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "docker is not installed"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

build_image() {
    log_info "Building Docker image..."
    docker build -t ${IMAGE}:${TAG} -t ${IMAGE}:latest .
    log_info "Docker image built successfully"
}

push_image() {
    log_info "Pushing Docker image to registry..."
    docker push ${IMAGE}:${TAG}
    docker push ${IMAGE}:latest
    log_info "Docker image pushed successfully"
}

deploy_kubernetes() {
    local env=$1
    
    log_info "Deploying to ${env} environment..."
    
    # Apply namespace
    kubectl apply -f kubernetes/namespace.yaml
    
    # Apply config and secrets
    kubectl apply -f kubernetes/configmap.yaml -n ${NAMESPACE}
    
    # Apply deployment
    kubectl apply -f kubernetes/deployment.yaml -n ${NAMESPACE}
    
    # Apply services
    kubectl apply -f kubernetes/service.yaml -n ${NAMESPACE}
    
    # Update image
    kubectl set image deployment/agentic-ai agentic-ai=${IMAGE}:${TAG} -n ${NAMESPACE}
    
    # Wait for rollout
    log_info "Waiting for deployment to complete..."
    kubectl rollout status deployment/agentic-ai -n ${NAMESPACE}
    
    log_info "Deployment to ${env} complete!"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pods
    kubectl get pods -n ${NAMESPACE} -l app=agentic-ai
    
    # Check services
    kubectl get services -n ${NAMESPACE}
    
    # Check ingress
    kubectl get ingress -n ${NAMESPACE}
    
    # Health check
    local endpoint=$(kubectl get ingress agentic-ai-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")
    log_info "Testing health endpoint..."
    
    if curl -sf http://${endpoint}/health > /dev/null 2>&1; then
        log_info "Health check passed!"
    else
        log_warn "Health check failed - deployment may still be starting up"
    fi
}

# Main script
main() {
    local environment=${1:-dev}
    
    log_info "Starting deployment to ${environment}..."
    
    check_prerequisites
    build_image
    push_image
    deploy_kubernetes ${environment}
    verify_deployment
    
    log_info "Deployment complete! 🎉"
}

# Run main script
main "$@"
