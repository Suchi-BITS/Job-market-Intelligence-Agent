from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PACKAGE_ROOT / "data" / "processed" / "jobs.csv"
DEFAULT_OUTPUT_DIR = PACKAGE_ROOT / "outputs"

REQUIRED_COLUMNS = ("title",)
OPTIONAL_COLUMNS = (
    "source", "job_id", "company", "location", "description",
    "employment_type", "tags", "remote", "salary", "published_at",
    "url", "experience_years_min",
)
SEARCHABLE_COLUMNS = ("title", "company", "description", "tags")
