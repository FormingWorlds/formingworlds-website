#!/usr/bin/env python3
"""Promote all lay_summary_draft fields to lay_summary."""

import yaml
import os

YAML_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "publications.yaml")

with open(YAML_PATH) as f:
    pubs = yaml.safe_load(f)

promoted = 0
for p in pubs:
    draft = p.get("lay_summary_draft")
    if draft and not p.get("lay_summary"):
        p["lay_summary"] = draft
        promoted += 1

with open(YAML_PATH, "w") as f:
    yaml.dump(pubs, f, default_flow_style=False, allow_unicode=True,
              width=120, sort_keys=False)

print(f"Promoted {promoted} lay summaries.")
