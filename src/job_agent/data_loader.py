import csv
from pathlib import Path
from typing import Dict, List

from .config import OPTIONAL_COLUMNS, REQUIRED_COLUMNS

Job = Dict[str, str]

class DataLoadError(RuntimeError):
    """Raised when a job CSV cannot be loaded or validated."""

def load_jobs(path: str | Path) -> List[Job]:
    """Load job records from CSV and normalize missing optional columns."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise DataLoadError(
            f"Job data file not found: {csv_path}. Check --data or restore the CSV."
        )
    if not csv_path.is_file():
        raise DataLoadError(f"Data path is not a file: {csv_path}")

    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            if not headers:
                raise DataLoadError(f"CSV has no header row: {csv_path}")
            missing = [column for column in REQUIRED_COLUMNS if column not in headers]
            if missing:
                raise DataLoadError(
                    f"CSV is missing required column(s): {', '.join(missing)}"
                )

            jobs = []
            for raw in reader:
                if not raw or not any((value or "").strip() for value in raw.values()):
                    continue
                job = {key: (value or "").strip() for key, value in raw.items() if key}
                for column in OPTIONAL_COLUMNS:
                    job.setdefault(column, "")
                if job.get("title"):
                    jobs.append(job)
            return jobs
    except UnicodeDecodeError as exc:
        raise DataLoadError(f"Could not decode {csv_path}. Save it as UTF-8 CSV.") from exc
    except OSError as exc:
        raise DataLoadError(f"Could not read {csv_path}: {exc}") from exc
