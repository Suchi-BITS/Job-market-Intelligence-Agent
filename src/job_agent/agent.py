from dataclasses import dataclass
from typing import List, Optional

from .data_loader import Job, load_jobs
from .search import search_jobs

@dataclass
class SearchRequest:
    query: str = ""
    location: str = ""
    remote_only: bool = False
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    limit: Optional[int] = None

@dataclass
class SearchResponse:
    total_matches: int
    shown_count: int
    jobs: List[Job]
    message: str

class JobSearchAgent:
    """Route a structured search request to the job-search tool."""
    def __init__(self, data_path):
        self.data_path = data_path

    def run(self, request: SearchRequest) -> SearchResponse:
        if request.min_experience is not None and request.min_experience < 0:
            raise ValueError("Minimum experience cannot be negative.")
        if request.max_experience is not None and request.max_experience < 0:
            raise ValueError("Maximum experience cannot be negative.")
        if (request.min_experience is not None and request.max_experience is not None
                and request.min_experience > request.max_experience):
            raise ValueError("Minimum experience cannot exceed maximum experience.")
        if request.limit is not None and request.limit < 1:
            raise ValueError("Limit must be at least 1.")

        jobs = load_jobs(self.data_path)
        matches = search_jobs(
            jobs, query=request.query, location=request.location,
            remote_only=request.remote_only,
            min_experience=request.min_experience,
            max_experience=request.max_experience,
        )
        total = len(matches)
        shown = matches[:request.limit] if request.limit else matches
        message = (
            "No jobs matched these filters. Try broader keywords or remove a filter."
            if not total else f"Found {total} matching job(s); displaying {len(shown)}."
        )
        return SearchResponse(total, len(shown), shown, message)
