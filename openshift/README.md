# OpenShift Deployment Guide

This guide explains how to deploy the Chaos Engineering application to OpenShift.

## Prerequisites

1. OpenShift CLI (`oc`) installed
2. Access to an OpenShift cluster
3. Docker registry access
4. Application container image built and pushed to registry

## Deployment Steps

1. Login to OpenShift:
   ```bash
   oc login <cluster-url>
   ```

2. Create a new project (if needed):
   ```bash
   oc new-project chaos-engineering
   ```

3. Deploy the application:
   ```bash
   oc apply -f deployment.yaml
   ```

4. Check deployment status:
   ```bash
   oc get pods
   oc get services
   oc get routes
   ```

## Configuration

The deployment configuration includes:
- Deployment with 3 replicas
- Service for internal communication
- Route for external access
- Resource limits and requests
- TLS-enabled route

## Scaling

To scale the deployment:
```bash
oc scale deployment chaos-engineering-app --replicas=<number>
```

## Monitoring

View application logs:
```bash
oc logs -f deployment/chaos-engineering-app
```

## Cleanup

To remove the deployment:
```bash
oc delete -f deployment.yaml
```
