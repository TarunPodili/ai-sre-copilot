# Incident INC-005

## Problem
The API deployment completed, but users received HTTP 503 responses.

## Symptoms
- HTTP 503
- Service unavailable
- Kubernetes pods running
- Requests failing

## Root Cause
The Kubernetes service had no healthy backend endpoints because the readiness probe was failing.

## Evidence
- Pods were running
- Readiness probe returned failure
- Service endpoint list was empty

## Resolution
Corrected the readiness probe configuration and redeployed.

## Prevention
Validate readiness probes during deployment testing.