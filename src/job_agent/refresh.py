"""Optional, best-effort refresh from public job-board feeds.

This is separate from local search, which does not require internet access.
Check provider terms and current API documentation before use.
"""
import argparse
import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from .experience import extract_experience_years

FIELDS = [
    "source", "job_id", "title", "company", "location", "description",
    "employment_type", "tags", "remote", "salary", "published_at", "url",
    "experience_years_min", "collected_at_utc",
]

def clean_html(value):
    text = str(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def request_json(url, params=None):
    try:
        import requests
    except ImportError as exc:
        raise RuntimeError(
            'Online refresh requires requests. Run: python -m pip install -e ".[refresh]"'
        ) from exc
    response = requests.get(
        url, params=params, timeout=25,
        headers={"User-Agent": "JobMarketIntelligenceLearningProject/1.0"}
    )
    response.raise_for_status()
    return response.json()

def fetch_arbeitnow(max_pages=5):
    rows = []
    url = "https://www.arbeitnow.com/api/job-board-api"
    for _ in range(max_pages):
        payload = request_json(url)
        if not isinstance(payload, dict) or not isinstance(payload.get("data", []), list):
            raise RuntimeError("Arbeitnow returned an unexpected response.")
        for item in payload.get("data", []):
            if not isinstance(item, dict):
                continue
            description = clean_html(item.get("description"))
            tags = item.get("tags", [])
            job_types = item.get("job_types", [])
            rows.append({
                "source": "Arbeitnow",
                "job_id": str(item.get("slug") or item.get("id") or ""),
                "title": clean_html(item.get("title")),
                "company": clean_html(item.get("company_name")),
                "location": clean_html(item.get("location")),
                "description": description,
                "employment_type": clean_html(", ".join(job_types) if isinstance(job_types, list) else job_types),
                "tags": ", ".join(map(str, tags)) if isinstance(tags, list) else clean_html(tags),
                "remote": str(item.get("remote", "")),
                "salary": str(item.get("salary") or ""),
                "published_at": str(item.get("created_at") or ""),
                "url": str(item.get("url") or item.get("job_url") or ""),
                "experience_years_min": str(extract_experience_years(description) or ""),
            })
        links = payload.get("links", {})
        next_url = links.get("next") if isinstance(links, dict) else None
        if not next_url:
            break
        url = next_url
    return rows

def fetch_remotive(limit=500):
    payload = request_json("https://remotive.com/api/remote-jobs", {"limit": limit})
    if not isinstance(payload, dict) or not isinstance(payload.get("jobs", []), list):
        raise RuntimeError("Remotive returned an unexpected response.")
    rows = []
    for item in payload.get("jobs", []):
        if not isinstance(item, dict):
            continue
        description = clean_html(item.get("description"))
        tags = item.get("tags", [])
        rows.append({
            "source": "Remotive",
            "job_id": str(item.get("id") or ""),
            "title": clean_html(item.get("title")),
            "company": clean_html(item.get("company_name")),
            "location": clean_html(item.get("candidate_required_location")),
            "description": description,
            "employment_type": clean_html(item.get("job_type")),
            "tags": ", ".join(map(str, tags)) if isinstance(tags, list) else clean_html(tags),
            "remote": "true",
            "salary": clean_html(item.get("salary")),
            "published_at": str(item.get("publication_date") or ""),
            "url": str(item.get("url") or item.get("job_url") or ""),
            "experience_years_min": str(extract_experience_years(description) or ""),
        })
    return rows

def main(argv=None):
    parser = argparse.ArgumentParser(description="Optional refresh of public job-board data.")
    parser.add_argument("--output", default="data/processed/jobs.csv")
    parser.add_argument("--max-entries", type=int, default=500)
    args = parser.parse_args(argv)
    if args.max_entries < 1:
        parser.error("--max-entries must be at least 1")

    rows, errors = [], []
    try:
        part = fetch_arbeitnow(max_pages=max(1, min(10, (args.max_entries + 49) // 50)))
        rows.extend(part)
        print(f"Arbeitnow: collected {len(part)} row(s).")
    except Exception as exc:
        errors.append(f"Arbeitnow: {type(exc).__name__}: {exc}")
        print(errors[-1], file=sys.stderr)
    try:
        part = fetch_remotive(limit=args.max_entries)
        rows.extend(part)
        print(f"Remotive: collected {len(part)} row(s).")
    except Exception as exc:
        errors.append(f"Remotive: {type(exc).__name__}: {exc}")
        print(errors[-1], file=sys.stderr)

    if not rows:
        print("No data collected; existing output was not overwritten.", file=sys.stderr)
        return 1

    collected = datetime.now(timezone.utc).isoformat()
    unique, seen = [], set()
    for row in rows:
        row["collected_at_utc"] = collected
        key = (row["source"], row["url"] or row["job_id"] or row["title"])
        if key not in seen:
            seen.add(key)
            unique.append(row)

    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(unique)
    print(f"Saved {len(unique)} unique row(s) to {destination.resolve()}.")
    if errors:
        print("Refresh completed partially; one or more sources failed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
