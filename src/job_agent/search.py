import re
from typing import Dict, Iterable, List, Optional

from .config import SEARCHABLE_COLUMNS
from .experience import extract_experience_years

Job = Dict[str, str]

def _truthy(value: str) -> bool:
    return (value or "").strip().lower() in {"true", "yes", "1", "remote", "y"}

def _query_groups(query: str) -> List[List[str]]:
    """Parse AND terms with OR alternatives, for example 'Python OR RAG'."""
    alternatives = re.split(r"\s+OR\s+", (query or "").strip(), flags=re.I)
    groups = []
    for alternative in alternatives:
        terms = [term.lower() for term in re.findall(r"[A-Za-z0-9+#.]+", alternative)]
        if terms:
            groups.append(terms)
    return groups

def _text_for(job: Job, columns: Iterable[str]) -> str:
    return " ".join((job.get(column, "") or "") for column in columns).lower()

def _experience(job: Job) -> Optional[int]:
    raw = (job.get("experience_years_min") or "").strip()
    if raw:
        try:
            return int(float(raw))
        except (TypeError, ValueError):
            pass
    return extract_experience_years(
        " ".join((job.get("title", ""), job.get("description", "")))
    )

def search_jobs(
    jobs: List[Job],
    query: str = "",
    location: str = "",
    remote_only: bool = False,
    min_experience: Optional[int] = None,
    max_experience: Optional[int] = None,
) -> List[Job]:
    """Search jobs with deterministic filters; unknown experience won't match ranges."""
    groups = _query_groups(query)
    results = []

    for job in jobs:
        searchable = _text_for(job, SEARCHABLE_COLUMNS)
        if groups and not any(all(term in searchable for term in group) for group in groups):
            continue
        if location and location.lower() not in (job.get("location") or "").lower():
            continue
        if remote_only:
            remote_text = " ".join((
                job.get("remote", ""), job.get("location", ""), job.get("description", "")
            )).lower()
            if not _truthy(job.get("remote", "")) and "remote" not in remote_text:
                continue

        years = _experience(job)
        if min_experience is not None or max_experience is not None:
            if years is None:
                continue
            if min_experience is not None and years < min_experience:
                continue
            if max_experience is not None and years > max_experience:
                continue

        title = (job.get("title") or "").lower()
        query_text = (query or "").lower().strip()
        if query_text and title == query_text:
            rank = 0
        elif query_text and any(term in title for group in groups for term in group):
            rank = 1
        else:
            rank = 2
        results.append((rank, job))

    results.sort(key=lambda pair: (
        pair[0], (pair[1].get("title") or "").lower(),
        (pair[1].get("company") or "").lower()
    ))
    return [job for _, job in results]
