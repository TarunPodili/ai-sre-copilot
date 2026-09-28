# Incident INC-001

## Problem
Order service failed during deployment because it could not connect to PostgreSQL.

## Symptoms
- Database connection timeout
- Application startup failure
- CrashLoopBackOff
- Deployment failed

## Root Cause
The application was configured with an incorrect database endpoint.

## Evidence
- PostgreSQL connection attempts timed out
- Other services were able to reach the database
- Application configuration contained an outdated database hostname

## Resolution
Updated the database endpoint in the application configuration and redeployed.

## Prevention
Validate database connectivity during deployment health checks.