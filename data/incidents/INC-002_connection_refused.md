# Incident INC-002

## Problem
Payment service failed to start because the database connection was refused.

## Symptoms
- Connection refused
- Application startup failure
- Container restart
- Deployment failure

## Root Cause
The PostgreSQL service was unavailable during deployment.

## Evidence
- Database port was unreachable
- PostgreSQL service was restarting
- Connection attempts were immediately refused

## Resolution
Restored the PostgreSQL service and restarted the application deployment.

## Prevention
Add database availability checks before application deployment.