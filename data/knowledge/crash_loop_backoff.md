# CrashLoopBackOff

## Description

A Kubernetes container repeatedly starts and crashes.

## Common Causes

- Application startup failure
- Invalid configuration
- Missing environment variable
- Dependency unavailable
- Application exception
- Incorrect startup command

## Evidence

Typical messages:

- CrashLoopBackOff
- Back-off restarting failed container
- Application startup failed

## Diagnostic Steps

1. Check container logs.
2. Inspect pod events.
3. Verify environment variables.
4. Check application configuration.
5. Check dependent services.

## Recommended Commands

kubectl logs <pod-name>

kubectl describe pod <pod-name>

## Remediation

Identify and fix the application startup failure.

## Prevention

Add startup validation and health checks.