# HTTP 503 Service Unavailable

A service is temporarily unavailable.

Common Causes:
- Service overloaded
- No healthy backend instances
- Deployment failure
- Health check failure

Evidence:
- HTTP 503
- Service Unavailable
- no healthy upstream

Diagnostics:
- Check pod health
- Check service endpoints
- Check deployment status

Remediation:
Restore healthy service instances.