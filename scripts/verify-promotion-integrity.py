#!/usr/bin/env python3
from pathlib import Path
import re
import sys
import yaml

BASE = Path("apps/helpdesk/overlays")
IMAGES = {
    "ghcr.io/awais-clouddev/gitops-cicd-deployment-platform-api",
    "ghcr.io/awais-clouddev/gitops-cicd-deployment-platform-frontend",
}

def read_digests(environment):
    path = BASE / environment / "kustomization.yaml"
    data = yaml.safe_load(path.read_text())
    result = {}

    for image in data.get("images", []):
        name = image.get("name")
        if name in IMAGES:
            digest = image.get("digest", "")
            if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
                raise SystemExit(f"Invalid digest: {name} in {environment}")
            if name in result:
                raise SystemExit(f"Duplicate image: {name}")
            result[name] = digest

    if set(result) != IMAGES:
        raise SystemExit(f"Missing required images in {environment}")

    return result

development = read_digests("development")
staging = read_digests("staging")

for name in sorted(IMAGES):
    print(f"{name}: {'PASS' if development[name] == staging[name] else 'FAIL'}")

if development != staging:
    sys.exit("PROMOTION INTEGRITY: FAIL")

print("PROMOTION INTEGRITY: PASS")
