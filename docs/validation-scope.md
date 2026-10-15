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

The existing local cluster could not start because Docker reported missing
container storage layers. Current clean installation, reconciliation and
runtime promotion checks remain blocked. Historical deployment evidence
does not verify the revised application.

Runtime Secrets remain outside Git. Both PostgreSQL and API require
database-name, database-user and database-password in helpdesk-secrets.
