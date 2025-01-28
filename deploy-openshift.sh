#!/bin/bash

# Exit on error
set -e

# Configuration
IMAGE_NAME="chaos-thinker"
IMAGE_TAG="latest"
OPENSHIFT_NAMESPACE="chaos-thinker"

# Login to OpenShift (uncomment and modify as needed)
# oc login --token=<token> --server=<server>

# Create namespace if it doesn't exist
oc new-project $OPENSHIFT_NAMESPACE 2>/dev/null || true

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# Tag for OpenShift registry
REGISTRY=$(oc get route default-route -n openshift-image-registry --template='{{ .spec.host }}')
docker tag $IMAGE_NAME:$IMAGE_TAG $REGISTRY/$OPENSHIFT_NAMESPACE/$IMAGE_NAME:$IMAGE_TAG

# Push to OpenShift registry
echo "Pushing image to OpenShift registry..."
docker push $REGISTRY/$OPENSHIFT_NAMESPACE/$IMAGE_NAME:$IMAGE_TAG

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
oc apply -f k8s/configmap.yaml
oc apply -f k8s/pvc.yaml
oc apply -f k8s/deployment.yaml
oc apply -f k8s/service.yaml
oc apply -f k8s/route.yaml

# Wait for deployment
echo "Waiting for deployment to complete..."
oc rollout status deployment/chaos-thinker

# Get the route URL
ROUTE_URL=$(oc get route chaos-thinker -o jsonpath='{.spec.host}')
echo "Application is deployed at: https://$ROUTE_URL"
