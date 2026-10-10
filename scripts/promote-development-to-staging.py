#!/usr/bin/env python3
from pathlib import Path
import re
import yaml

DEV = Path("apps/helpdesk/overlays/development/kustomization.yaml")
STAGING = Path("apps/helpdesk/overlays/staging/kustomization.yaml")

api = "ghcr.io/awais-clouddev/gitops-cicd-deployment-platform-api"
frontend = "ghcr.io/awais-clouddev/gitops-cicd-deployment-platform-frontend"

dev = yaml.safe_load(DEV.read_text())
staging = yaml.safe_load(STAGING.read_text())

def image_digests(data):
    images = data.get("images", [])
    result = {}
    for image in images:
        name = image.get("name")
        if name in (api, frontend):
            digest = image.get("digest", "")
            if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
                raise SystemExit(f"Invalid digest for {name}")
            result[name] = digest
    if set(result) != {api, frontend}:
        raise SystemExit("Missing API or frontend image")
    return result

source = image_digests(dev)
image_digests(staging)

for image in staging["images"]:
    if image["name"] in source:
        image["digest"] = source[image["name"]]

STAGING.write_text(yaml.safe_dump(staging, sort_keys=False))
print("PASS: Staging promoted using development image digests")
