# OOMKilled

## Description

A container was terminated because it exceeded its memory limit.

## Common Causes

- Memory leak
- Insufficient memory limit
- Large workload
- Inefficient application behavior

## Evidence

Typical messages:

- OOMKilled
- Out of memory
- Container killed

## Diagnostic Steps

1. Check container memory usage.
2. Review resource limits.
3. Check for memory leaks.
4. Review workload size.

## Recommended Commands

kubectl describe pod <pod-name>

kubectl top pod <pod-name>

## Remediation

Optimize memory usage or increase the container memory limit.

## Prevention

Configure appropriate resource requests and limits and monitor memory usage.