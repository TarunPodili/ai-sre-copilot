# Incident INC-004

## Problem
Payment API deployment failed because Kubernetes could not pull the container image.

## Symptoms
- Failed to pull image
- ErrImagePull
- ImagePullBackOff
- Deployment failed

## Root Cause
The deployment referenced an incorrect container image tag.

## Evidence
- Image payment-api:v1.7 did not exist in the registry
- Registry was available
- Authentication was successful

## Resolution
Updated the deployment manifest to use the correct image tag.

## Prevention
Validate container image existence during CI/CD before deployment.