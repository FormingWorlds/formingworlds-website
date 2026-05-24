#!/usr/bin/env python3
"""Retry ADS abstract fetch for entries that failed the bibcode lookup.

Uses title+author queries to find published versions of arXiv preprints.
Updates both abstract and bibcode in the YAML.
"""

import os
import time
import yaml
import requests

ADS_TOKEN = os.environ.get("ADS_DEV_KEY") or os.environ.get("ADS_API_TOKEN")
if not ADS_TOKEN:
    raise SystemExit("Set ADS_DEV_KEY or ADS_API_TOKEN")

ADS_API = "https://api.adsabs.harvard.edu/v1"
HEADERS = {"Authorization": f"Bearer {ADS_TOKEN}"}
YAML_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "publications.yaml")

RETRY_QUERIES = {
    "nicholls-2026-volatile-rich": 'title:"Volatile-rich evolution of molten super-Earth" first_author:Nicholls',
    "nicholls-2025-self-limited": 'title:"Self-limited tidal heating" first_author:Nicholls',
    "cesario-2024-large": 'title:"Large Interferometer For Exoplanets" first_author:Cesario year:2024',
    "lichtenberg-2025-constraining": 'title:"Constraining exoplanet interiors" first_author:Lichtenberg',
    "lichtenberg-2025-super-earths": 'title:"Super-Earths and Earth-like Exoplanets" first_author:Lichtenberg',
    "lichtenberg-2023-geophysical": 'title:"Geophysical Evolution During Rocky Planet" first_author:Lichtenberg',
}


def main():
    with open(YAML_PATH) as f:
        pubs = yaml.safe_load(f)

    for slug, query in RETRY_QUERIES.items():
        p = next((x for x in pubs if x["slug"] == slug), None)
        if not p:
            print(f"SKIP {slug}: not found in YAML")
            continue
        if p.get("abstract"):
            print(f"SKIP {slug}: already has abstract")
            continue

        r = requests.get(
            f"{ADS_API}/search/query",
            headers=HEADERS,
            params={"q": query, "fl": "abstract,bibcode,title,pub", "rows": 3},
        )
        r.raise_for_status()
        docs = r.json().get("response", {}).get("docs", [])

        # Pick best match (journal article preferred over arXiv/proceeding)
        best = None
        for d in docs:
            if d.get("abstract"):
                if best is None:
                    best = d
                elif "arXiv" not in d["bibcode"] and "arXiv" in best["bibcode"]:
                    best = d

        if best:
            p["abstract"] = best["abstract"]
            old_bc = p.get("bibcode")
            new_bc = best["bibcode"]
            if old_bc != new_bc:
                p["bibcode"] = new_bc
                print(f"OK {slug}: bibcode {old_bc} -> {new_bc}")
            else:
                print(f"OK {slug}")
        else:
            print(f"MISS {slug}")

        time.sleep(0.3)

    with open(YAML_PATH, "w") as f:
        yaml.dump(pubs, f, default_flow_style=False, allow_unicode=True,
                  width=120, sort_keys=False)

    print("\nDone.")


if __name__ == "__main__":
    main()
