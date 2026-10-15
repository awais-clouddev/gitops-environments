#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
IMAGES = {
    "ghcr.io/awais-clouddev/gitops-cicd-deployment-platform-api",
    "ghcr.io/awais-clouddev/gitops-cicd-deployment-platform-frontend",
}

for environment in ("development", "staging"):
    overlay = ROOT / "apps/helpdesk/overlays" / environment
    config = yaml.safe_load((overlay / "kustomization.yaml").read_text())
    expected_namespace = f"helpdesk-{environment}"
    assert config["namespace"] == expected_namespace
    found = {}
    for image in config.get("images", []):
        name = image["name"]
        if name in IMAGES:
            assert name not in found, f"Duplicate image: {name}"
            assert image.get("newName", name) == name
            assert re.fullmatch(r"sha256:[a-f0-9]{64}", image.get("digest", ""))
            found[name] = image["digest"]
    assert set(found) == IMAGES, f"Missing application images: {environment}"

    rendered = subprocess.check_output(
        ["kubectl", "kustomize", str(overlay)], text=True
    )
    documents = [doc for doc in yaml.safe_load_all(rendered) if doc]
    refs = set()
    application_images = set()
    for doc in documents:
        if doc["kind"] in ("Deployment", "StatefulSet"):
            assert doc["metadata"]["namespace"] == expected_namespace
            for container in doc["spec"]["template"]["spec"]["containers"]:
                image = container["image"]
                for name in IMAGES:
                    if image.startswith(name + "@"):
                        assert image == name + "@" + found[name]
                        application_images.add(name)
                for entry in container.get("env", []):
                    ref = entry.get("valueFrom", {}).get("secretKeyRef")
                    if ref:
                        assert ref["name"] == "helpdesk-secrets"
                        refs.add(ref["key"])
    assert application_images == IMAGES
    assert refs == {"database-name", "database-user", "database-password"}
    print(f"PASS: {environment} rendering, namespaces, digests and Secret keys")
