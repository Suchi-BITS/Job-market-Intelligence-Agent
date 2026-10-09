import argparse
import csv
import sys
from pathlib import Path

from .agent import JobSearchAgent, SearchRequest
from .config import DEFAULT_DATA_PATH
from .data_loader import DataLoadError
from .experience import extract_experience_years

def build_parser():
    parser = argparse.ArgumentParser(
        prog="job-agent",
        description="Search saved job-board listings with a simple Python agent.",
    )
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH), help="Path to jobs CSV.")
    parser.add_argument("--query", default="", help='Search terms; use "OR" for alternatives.')
    parser.add_argument("--location", default="", help="Substring to match in job location.")
    parser.add_argument("--remote", action="store_true", help="Only show remote jobs.")
    parser.add_argument("--min-experience", type=int, default=None)
    parser.add_argument("--max-experience", type=int, default=None)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--export", default="", help="Optional path to export matching jobs as CSV.")
    return parser

def print_jobs(jobs):
    if not jobs:
        print("No matching records to display.")
        return
    for index, job in enumerate(jobs, start=1):
        years = (job.get("experience_years_min") or "").strip()
        if years:
            experience = f"{years}+ years (stored hint)"
        else:
            years = extract_experience_years(
                f"{job.get('title', '')} {job.get('description', '')}"
            )
            experience = f"{years}+ years (text hint)" if years is not None else "Not stated"
        print(f"\n{index}. {job.get('title') or '(untitled)'}")
        print(f"   Company: {job.get('company') or 'Not provided'}")
        print(f"   Location: {job.get('location') or 'Not provided'}")
        print(f"   Experience: {experience}")
        print(f"   Remote: {job.get('remote') or 'Not specified'}")
        if job.get("salary"):
            print(f"   Salary: {job['salary']}")
        if job.get("published_at"):
            print(f"   Published: {job['published_at']}")
        print(f"   Source: {job.get('source') or 'Not specified'}")
        print(f"   URL: {job.get('url') or 'No URL provided'}")

def export_csv(path, jobs):
    destination = Path(path)
    if not destination.is_absolute():
        destination = Path.cwd() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = list(jobs[0].keys()) if jobs else [
        "source", "job_id", "title", "company", "location", "description",
        "employment_type", "tags", "remote", "salary", "published_at",
        "url", "experience_years_min"
    ]
    with destination.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(jobs)
    return destination

def interactive_request():
    print("Job Market Intelligence Agent — local CSV search")
    query = input("Job role or keyword (e.g. AI Engineer): ").strip()
    location = input("Location filter (press Enter to skip): ").strip()
    remote = input("Remote jobs only? [y/N]: ").strip().lower() in {"y", "yes"}
    return SearchRequest(query=query, location=location, remote_only=remote, limit=20)

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if len(sys.argv) == 1 and argv is None:
            request = interactive_request()
            data_path = DEFAULT_DATA_PATH
            export_path = ""
        else:
            request = SearchRequest(
                query=args.query, location=args.location, remote_only=args.remote,
                min_experience=args.min_experience, max_experience=args.max_experience,
                limit=args.limit,
            )
            data_path, export_path = args.data, args.export

        response = JobSearchAgent(data_path).run(request)
        print("\n" + response.message)
        print_jobs(response.jobs)
        if export_path:
            saved = export_csv(export_path, response.jobs)
            print(f"\nExported {len(response.jobs)} record(s) to: {saved}")
        return 0
    except (DataLoadError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
