# Incident INC-003

## Problem
Recommendation service repeatedly crashed after deployment.

## Symptoms
- High memory usage
- OOMKilled
- Container restart
- CrashLoopBackOff

## Root Cause
The container exceeded its configured Kubernetes memory limit while loading the ML model.

## Evidence
- Memory usage exceeded 95 percent
- Kubernetes reported OOMKilled
- Model loading occurred immediately before termination

## Resolution
Increased the container memory limit and optimized model loading.

## Prevention
Monitor memory usage and test model memory requirements before deployment.