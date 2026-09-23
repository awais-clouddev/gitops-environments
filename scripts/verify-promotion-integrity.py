#!/usr/bin/env python3

from pathlib import Path
import re
import sys

DEV = Path("apps/helpdesk/overlays/development/kustomization.yaml")
STAGING = Path("apps/helpdesk/overlays/staging/kustomization.yaml")

IMAGES = [
    "gitops-cicd-deployment-platform-api",
    "gitops-cicd-deployment-platform-frontend",
]


def digest_for(path, image):
    text = path.read_text()

    pattern = (
        rf"name:\s+ghcr\.io/awais-clouddev/{re.escape(image)}.*?"
        rf"digest:\s+(sha256:[a-f0-9]{{64}})"
    )

    match = re.search(pattern, text, re.S)

    if not match:
        raise SystemExit(f"Missing immutable digest for {image} in {path}")

    return match.group(1)


failed = False

for image in IMAGES:
    dev = digest_for(DEV, image)
    staging = digest_for(STAGING, image)

    print(f"{image}")
    print(f"  development: {dev}")
    print(f"  staging:     {staging}")

    if dev != staging:
        print("  RESULT: FAIL - artifacts differ")
        failed = True
    else:
        print("  RESULT: PASS - identical immutable artifact")

if failed:
    sys.exit(1)

print()
print("PROMOTION INTEGRITY: PASS")
print("Development and staging use the exact same image digests.")
