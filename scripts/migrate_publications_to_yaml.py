#!/usr/bin/env python3
"""Parse content/publications/_index.md into data/publications.yaml.

The markdown source stores each paper as a one-paragraph entry with bolded
lab-member names. This script extracts authors, title, links, venue prose,
year, and the SciX/ADS bibcode into a structured YAML data file that the
Hugo template iterates over.

Each entry preserves the original markdown line under ``_raw`` so a stray
parse can be spot-checked against the source.

Lab-led detection: a paper is flagged ``lab_led: true`` if the first author
in the author list is wrapped in ``**...**`` (the project's existing
convention for lab members).

Run with the miniforge base interpreter (has pyyaml + requests):

    /Users/timlichtenberg/miniforge3/bin/python \\
        scripts/migrate_publications_to_yaml.py
"""

from __future__ import annotations

import re
import sys
import unicodedata
import urllib.parse
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "content" / "publications" / "_index.md"
DST = REPO / "data" / "publications.yaml"

SECTION_SLUGS = {
    "Research Articles": "research",
    "Reviews": "reviews",
    "Perspectives & White Papers": "perspectives",
    "Numerical Methods & Instrumentation": "instrumentation",
    "Theses": "theses",
}
SUBSECTION_SLUGS = {
    "Preprints": "preprints",
    "Published & Accepted": "published",
}

LINK_RE = re.compile(r"\[([^\]]+?)\]\(([^)]+)\)")
YEAR_RE = re.compile(r"\((\d{4})\)")
MONTH_YEAR_RE = re.compile(r"\(\d{1,2}/(\d{4})\)")
SCIX_RE = re.compile(r"scixplorer\.org/abs/([^/\s)]+)(?:/abstract)?")
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/([0-9]+\.[0-9]+(?:v\d+)?)")
DOI_RE = re.compile(r"doi\.org/(.+?)(?:[)\s]|$)")

EXTRA_LABELS = {"pdf", "blog", "video", "news", "article"}


def slugify(text: str) -> str:
    """Lowercase, ascii, dash-separated slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "untitled"


def first_author_lastname(authors_md: str) -> str:
    """Pull the last name of the first author from the markdown prefix.

    Author lists use the convention "LastName Initials" (e.g. "Lichtenberg T",
    "van Dijk MR"). The last name is everything up to the first all-uppercase
    initials token.
    """
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", authors_md)
    first = cleaned.split(",")[0].strip()
    first = re.sub(r"\s+(?:et al\.?|&.*)$", "", first).strip()
    tokens = [t for t in re.split(r"\s+", first) if t]
    if not tokens:
        return "anon"
    if len(tokens) == 1:
        return slugify(tokens[0])
    name_parts: list[str] = []
    for tok in tokens:
        if re.fullmatch(r"[A-Z]+[-.]?[A-Z]?\.?", tok):
            break
        name_parts.append(tok)
    if not name_parts:
        name_parts = tokens[:1]
    return slugify("-".join(name_parts))


def infer_year_from_arxiv(url: str) -> int | None:
    """ArXiv post-2007 IDs are YYMM.NNNNN; derive a 4-digit year."""
    m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{2})(\d{2})\.\d+", url)
    if not m:
        return None
    yy = int(m.group(1))
    return 2000 + yy


def detect_lab_led(authors_md: str) -> bool:
    """First author wrapped in **...** signals lab-led."""
    stripped = authors_md.lstrip()
    return stripped.startswith("**")


def classify_url(url: str) -> str | None:
    if "scixplorer.org/abs/" in url or "ui.adsabs.harvard.edu/abs/" in url:
        return "scix"
    if "arxiv.org/abs/" in url:
        return "arxiv"
    if "doi.org/" in url:
        return "doi"
    return None


def extract_bibcode(url: str) -> str | None:
    m = SCIX_RE.search(url)
    if not m:
        return None
    return urllib.parse.unquote(m.group(1))


def parse_paper_line(
    line: str, section: str, subsection: str | None
) -> dict | None:
    line = line.strip()
    if not line:
        return None

    links = list(LINK_RE.finditer(line))
    if not links:
        # Likely a thesis with no link (some BSc/MSc theses); still capture
        return parse_no_link_entry(line, section, subsection)

    first = links[0]
    authors_md = line[: first.start()].rstrip()
    if authors_md.endswith("."):
        authors_md = authors_md[:-1].rstrip()
    if authors_md.endswith(","):
        authors_md = authors_md[:-1].rstrip()

    title = first.group(1).strip()
    title = re.sub(r"\*([^*]+)\*", r"\1", title)
    title = title.rstrip(".")
    primary_url = first.group(2).strip()

    rest = line[first.end() :].lstrip(" .")

    extras: dict[str, str] = {}
    for m in links[1:]:
        label = m.group(1).strip().lower()
        url = m.group(2).strip()
        if label in EXTRA_LABELS:
            extras[label] = url

    last_extra = links[-1] if len(links) > 1 else first
    venue_md = line[first.end() : last_extra.start()].strip()
    venue_md = venue_md.rstrip(",").rstrip()
    if venue_md.endswith("."):
        venue_md = venue_md[:-1]
    venue_md = re.sub(r"\.\s*\[[^\]]+\]\([^)]+\),?\s*$", "", venue_md)

    year_match = None
    for m in YEAR_RE.finditer(line):
        year_match = m
    year = int(year_match.group(1)) if year_match else None
    if year is None:
        for url in [primary_url, *extras.values()]:
            year = infer_year_from_arxiv(url)
            if year:
                break

    typed_links: dict[str, str] = dict(extras)
    primary_kind = classify_url(primary_url)
    if primary_kind:
        typed_links.setdefault(primary_kind, primary_url)
    for label, url in list(typed_links.items()):
        kind = classify_url(url)
        if kind and kind != label and kind not in typed_links:
            typed_links[kind] = url

    bibcode = None
    for url in [primary_url, *extras.values()]:
        bibcode = extract_bibcode(url)
        if bibcode:
            break

    lab_led = detect_lab_led(authors_md)
    base = first_author_lastname(authors_md)
    title_word = next(
        (slugify(w) for w in title.split() if len(w) > 3), "paper"
    )
    slug = f"{base}-{year or 'nd'}-{title_word}"[:80]

    return {
        "slug": slug,
        "section": section,
        "subsection": subsection,
        "year": year,
        "authors_md": authors_md,
        "title": title,
        "venue_md": venue_md or None,
        "primary_url": primary_url,
        "links": typed_links,
        "bibcode": bibcode,
        "lab_led": lab_led,
        "abstract": None,
        "lay_summary": None,
        "lay_summary_draft": None,
        "_raw": line,
    }


def parse_no_link_entry(
    line: str, section: str, subsection: str | None
) -> dict | None:
    m = re.match(r"\*\*([^*]+)\*\*,\s*\*([^*]+)\*\.\s*(.*)$", line)
    if not m:
        return None
    authors_md = f"**{m.group(1)}**"
    title = m.group(2).strip().rstrip(".")
    venue_md = m.group(3).strip().rstrip(".")
    year_match = None
    for ym in YEAR_RE.finditer(line):
        year_match = ym
    year = int(year_match.group(1)) if year_match else None
    if year is None:
        my = MONTH_YEAR_RE.search(line)
        if my:
            year = int(my.group(1))
    base = first_author_lastname(authors_md)
    title_word = next(
        (slugify(w) for w in title.split() if len(w) > 3), "thesis"
    )
    slug = f"{base}-{year or 'nd'}-{title_word}"[:80]
    return {
        "slug": slug,
        "section": section,
        "subsection": subsection,
        "year": year,
        "authors_md": authors_md,
        "title": title,
        "venue_md": venue_md or None,
        "primary_url": None,
        "links": {},
        "bibcode": None,
        "lab_led": True,
        "abstract": None,
        "lay_summary": None,
        "lay_summary_draft": None,
        "_raw": line,
    }


def dedupe_slugs(entries: list[dict]) -> None:
    counts: dict[str, int] = {}
    seen: dict[str, int] = {}
    for e in entries:
        counts[e["slug"]] = counts.get(e["slug"], 0) + 1
    for e in entries:
        if counts[e["slug"]] > 1:
            seen[e["slug"]] = seen.get(e["slug"], 0) + 1
            e["slug"] = f"{e['slug']}-{seen[e['slug']]}"


def parse_markdown(path: Path) -> list[dict]:
    section = ""
    subsection: str | None = None
    entries: list[dict] = []
    for raw in path.read_text().splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            header = line[3:].strip()
            section = SECTION_SLUGS.get(header, slugify(header))
            subsection = None
            continue
        if line.startswith("### "):
            header = line[4:].strip()
            subsection = SUBSECTION_SLUGS.get(header, slugify(header))
            continue
        if line.startswith("#") or not line or line.startswith("---"):
            continue
        if not section:
            continue
        entry = parse_paper_line(line, section, subsection)
        if entry:
            entries.append(entry)
    dedupe_slugs(entries)
    return entries


def main() -> int:
    entries = parse_markdown(SRC)
    lab_led_count = sum(1 for e in entries if e["lab_led"])
    DST.parent.mkdir(parents=True, exist_ok=True)

    class LiteralStr(str):
        pass

    def literal_str_representer(dumper, data):
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str", data, style="|"
        )

    yaml.add_representer(LiteralStr, literal_str_representer)

    DST.write_text(
        yaml.safe_dump(
            entries,
            sort_keys=False,
            allow_unicode=True,
            width=1000,
            default_flow_style=False,
        )
    )
    sys.stdout.write(
        f"Wrote {len(entries)} entries to {DST.relative_to(REPO)} "
        f"({lab_led_count} lab-led)\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
