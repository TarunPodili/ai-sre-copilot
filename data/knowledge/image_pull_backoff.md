# ImagePullBackOff

## Description

Kubernetes cannot pull the container image required by a pod.

## Common Causes

- Invalid image name
- Invalid image tag
- Image does not exist
- Registry authentication failure
- Registry unavailable
- Network connectivity problems

## Evidence

Typical log messages:

- ImagePullBackOff
- ErrImagePull
- Failed to pull image
- Pull access denied

## Diagnostic Steps

1. Verify the image name and tag.
2. Check whether the image exists in the registry.
3. Check registry credentials.
4. Inspect Kubernetes pod events.
5. Verify network connectivity to the registry.

## Recommended Commands

kubectl describe pod <pod-name>

kubectl get events --sort-by=.lastTimestamp

## Remediation

Correct the image reference or registry credentials.

## Prevention

Add container image validation to the CI/CD pipeline.