#!/usr/bin/env python3
"""Fetch ADS abstracts for lab-led publications missing them."""

import os
import re
import time
import yaml
import requests

ADS_TOKEN = os.environ.get("ADS_DEV_KEY") or os.environ.get("ADS_API_TOKEN")
if not ADS_TOKEN:
    raise SystemExit("Set ADS_DEV_KEY or ADS_API_TOKEN")

ADS_API = "https://api.adsabs.harvard.edu/v1"
HEADERS = {"Authorization": f"Bearer {ADS_TOKEN}"}
YAML_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "publications.yaml")


def query_ads_by_bibcode(bibcode: str) -> str | None:
    """Fetch abstract from ADS by bibcode."""
    r = requests.get(
        f"{ADS_API}/search/query",
        headers=HEADERS,
        params={"q": f"bibcode:{bibcode}", "fl": "abstract", "rows": 1},
    )
    r.raise_for_status()
    docs = r.json().get("response", {}).get("docs", [])
    if docs and docs[0].get("abstract"):
        return docs[0]["abstract"]
    return None


def query_ads_by_arxiv(arxiv_id: str) -> str | None:
    """Fetch abstract from ADS by arXiv ID."""
    r = requests.get(
        f"{ADS_API}/search/query",
        headers=HEADERS,
        params={"q": f"arXiv:{arxiv_id}", "fl": "abstract,bibcode", "rows": 1},
    )
    r.raise_for_status()
    docs = r.json().get("response", {}).get("docs", [])
    if docs and docs[0].get("abstract"):
        return docs[0]["abstract"]
    return None


def query_ads_by_doi(doi: str) -> str | None:
    """Fetch abstract from ADS by DOI."""
    r = requests.get(
        f"{ADS_API}/search/query",
        headers=HEADERS,
        params={"q": f"doi:{doi}", "fl": "abstract,bibcode", "rows": 1},
    )
    r.raise_for_status()
    docs = r.json().get("response", {}).get("docs", [])
    if docs and docs[0].get("abstract"):
        return docs[0]["abstract"]
    return None


def extract_arxiv_id(url: str) -> str | None:
    """Extract arXiv ID from a URL like https://arxiv.org/abs/2605.03741."""
    m = re.search(r"arxiv.org/abs/(\d{4}\.\d+)", url)
    return m.group(1) if m else None


def extract_scix_bibcode(url: str) -> str | None:
    """Extract bibcode from a SciX URL."""
    m = re.search(r"/abs/([^/]+)", url)
    return m.group(1) if m else None


def extract_doi(url: str) -> str | None:
    """Extract DOI from a URL like https://doi.org/10.1234/..."""
    m = re.search(r"doi.org/(10\.\S+)", url)
    return m.group(1) if m else None


def main():
    with open(YAML_PATH) as f:
        pubs = yaml.safe_load(f)

    targets = [
        p for p in pubs
        if p.get("lab_led")
        and p.get("section") != "theses"
        and not p.get("abstract")
    ]
    print(f"Fetching abstracts for {len(targets)} entries...")

    fetched = 0
    failed = []

    for p in targets:
        slug = p["slug"]
        abstract = None

        # Try bibcode first
        if p.get("bibcode"):
            abstract = query_ads_by_bibcode(p["bibcode"])
        # Try extracting bibcode from SciX URL
        if not abstract:
            scix_url = p.get("links", {}).get("scix", "")
            if scix_url:
                bc = extract_scix_bibcode(scix_url)
                if bc:
                    abstract = query_ads_by_bibcode(bc)
        # Try arXiv
        if not abstract:
            arxiv_url = p.get("links", {}).get("arxiv", "")
            if arxiv_url:
                aid = extract_arxiv_id(arxiv_url)
                if aid:
                    abstract = query_ads_by_arxiv(aid)
        # Try DOI
        if not abstract:
            doi_url = p.get("links", {}).get("doi", "")
            if doi_url:
                doi = extract_doi(doi_url)
                if doi:
                    abstract = query_ads_by_doi(doi)

        if abstract:
            p["abstract"] = abstract
            fetched += 1
            print(f"  OK  {slug}")
        else:
            failed.append(slug)
            print(f"  MISS {slug}")

        time.sleep(0.3)

    with open(YAML_PATH, "w") as f:
        yaml.dump(pubs, f, default_flow_style=False, allow_unicode=True,
                  width=120, sort_keys=False)

    print(f"\nDone: {fetched} fetched, {len(failed)} failed")
    if failed:
        print("Failed entries:")
        for s in failed:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
