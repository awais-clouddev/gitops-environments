#!/usr/bin/env python3

from pathlib import Path
import re

DEV = Path("apps/helpdesk/overlays/development/kustomization.yaml")
STAGING = Path("apps/helpdesk/overlays/staging/kustomization.yaml")

if not DEV.exists():
    raise SystemExit(f"Missing: {DEV}")

if not STAGING.exists():
    raise SystemExit(f"Missing: {STAGING}")

dev_text = DEV.read_text()
staging_text = STAGING.read_text()

api_match = re.search(
    r'name:\s+ghcr\.io/awais-clouddev/gitops-cicd-deployment-platform-api.*?'
    r'digest:\s+(sha256:[a-f0-9]{64})',
    dev_text,
    re.S,
)

frontend_match = re.search(
    r'name:\s+ghcr\.io/awais-clouddev/gitops-cicd-deployment-platform-frontend.*?'
    r'digest:\s+(sha256:[a-f0-9]{64})',
    dev_text,
    re.S,
)

if not api_match or not frontend_match:
    raise SystemExit("Could not find immutable development digests")

api_digest = api_match.group(1)
frontend_digest = frontend_match.group(1)

marker = "\nimages:\n"

if marker in staging_text:
    staging_text = staging_text.split(marker)[0].rstrip() + "\n"

staging_text += f"""
images:
  - name: ghcr.io/awais-clouddev/gitops-cicd-deployment-platform-api
    newName: ghcr.io/awais-clouddev/gitops-cicd-deployment-platform-api
    digest: {api_digest}

  - name: ghcr.io/awais-clouddev/gitops-cicd-deployment-platform-frontend
    newName: ghcr.io/awais-clouddev/gitops-cicd-deployment-platform-frontend
    digest: {frontend_digest}
"""

STAGING.write_text(staging_text)

print("Promotion complete")
print(f"API:      {api_digest}")
print(f"Frontend: {frontend_digest}")
