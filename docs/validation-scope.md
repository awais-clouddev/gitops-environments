# Environment and Verification Scope

## Reconciliation

Development has a committed Argo CD Application with automatic sync,
pruning and self-healing.

Staging is desired-state-only in this repository. Promotion updates its
image digests; it does not establish a running staging deployment.
No staging Argo CD Application or staging reconciliation is claimed.

## Automated validation

Run from the repository root:

    python3 scripts/validate-overlays.py

Both overlays are rendered and checked for environment namespaces,
application image digests and runtime Secret-key references. GitHub Actions
runs the same checks on pushes and pull requests.

Rendering is an offline check, not Kubernetes API schema validation or
proof of healthy workloads.

Promotion copies development digests to staging. Run the promotion integrity
script immediately after promotion. Different digests between environments
are valid when staging intentionally retains an earlier release.

## Current verification

Local overlay validation passed. Promotion and matching image digests were
tested in a disposable copy without changing committed environment versions.

A fresh three-node kind cluster named gitops-audit was verified locally
on 15 October 2026 using Argo CD v3.5.3. Runtime Secrets used the documented
database keys. All five application Pods became Ready, and Argo CD reported
Synced and Healthy for source release
f5b376905d2325dd7d529888b4ee8fbea875325f.

Gateway HTTP tests passed for health, ticket creation, reading,
case-insensitive priority filtering, status update and verification.
After manually scaling the API to two replicas, Argo CD restored the
Git-declared count of one replica.

Redis failure behavior was verified using mocked regression tests.
A live Redis outage, browser rendering and staging runtime promotion were
not tested in this run. Staging remains desired-state-only.
The older cluster's Docker storage problem was bypassed with the fresh
audit cluster; it was not repaired.

Runtime Secrets remain outside Git. Both PostgreSQL and API require
database-name, database-user and database-password in helpdesk-secrets.
