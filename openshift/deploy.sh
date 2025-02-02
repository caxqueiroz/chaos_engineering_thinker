#!/bin/bash

# Exit on error
set -e

# Default values
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"docker.io/username"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
PROJECT_NAME=${PROJECT_NAME:-"chaos-engineering"}

# Check if oc is installed
if ! command -v oc &> /dev/null; then
    echo "Error: OpenShift CLI (oc) is not installed"
    exit 1
fi

# Check if logged in to OpenShift
if ! oc whoami &> /dev/null; then
    echo "Error: Not logged in to OpenShift. Please run 'oc login' first"
    exit 1
fi

# Create project if it doesn't exist
if ! oc get project "$PROJECT_NAME" &> /dev/null; then
    echo "Creating project $PROJECT_NAME"
    oc new-project "$PROJECT_NAME"
else
    echo "Using existing project $PROJECT_NAME"
    oc project "$PROJECT_NAME"
fi

# Replace variables in deployment yaml
echo "Deploying application..."
sed "s|\${DOCKER_REGISTRY}|$DOCKER_REGISTRY|g" deployment.yaml | oc apply -f -

# Wait for deployment to complete
echo "Waiting for deployment to complete..."
oc rollout status deployment/chaos-engineering-app

# Get the route URL
ROUTE_URL=$(oc get route chaos-engineering-route -o jsonpath='{.spec.host}')
echo "Application deployed successfully!"
echo "Access your application at: https://$ROUTE_URL"
