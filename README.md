# Job Market Intelligence Agent

A small, rule-based job-search agent built with plain Python. It searches a local CSV dataset by keywords, location, remote status, and explicitly stated experience requirements. It can export matching listings to CSV.

No LangChain, LangGraph, or LLM is used. The agent routes a user's structured request to ordinary Python functions, validates the data, and reports what it found.

## Features
- Search saved job-board listings by role or keyword.
- Optional location and remote-only filters.
- Optional minimum/maximum experience filters when experience is explicitly stated.
- Export matching listings to CSV.
- Optional refresh command for public Arbeitnow and Remotive feeds.
- Tests use Python's built-in `unittest`; they do not require internet access.
- Sample records are synthetic examples, not current vacancies.

## Requirements
- Python 3.10+
- Core local search uses only the standard library.
- `requests` is needed only for optional online refresh.

## Windows setup (Command Prompt)

```cmd
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e .
```

## Search examples

```cmd
python -m job_agent --query "AI Engineer"
python -m job_agent --query "Python OR RAG" --location India
python -m job_agent --query "machine learning" --remote
python -m job_agent --query "knowledge graph" --min-experience 3 --max-experience 6
python -m job_agent --query "data scientist" --limit 10 --export outputs\matching_jobs.csv
```

The query is case-insensitive. Terms separated by `OR` are alternatives. Without `OR`, all query terms must occur in the searchable text.

Interactive mode:

```cmd
python -m job_agent
```

Use a different CSV:

```cmd
python -m job_agent --data path\to\your_jobs.csv --query "AI Engineer"
```

## Optional online refresh

```cmd
python -m pip install -e ".[refresh]"
python -m job_agent.refresh --output data/processed/jobs.csv --max-entries 500
```

Refresh is best-effort and separate from normal search. It reports per-source failures and does not overwrite the dataset if no source returns data. Respect provider terms, rate limits, and attribution requirements.

## CSV schema

Required: `title`. Optional columns include `source`, `job_id`, `company`, `location`, `description`, `employment_type`, `tags`, `remote`, `salary`, `published_at`, `url`, and `experience_years_min`.

Experience is never guessed. Unknown experience remains blank; if an experience filter is specified, unknown records are excluded because the requirement cannot be verified.

## Tests

```cmd
python -m unittest discover -s tests -v
```

## Project layout

```text
job-market-intelligence-agent/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── .env.example
├── data/processed/jobs.csv
├── outputs/.gitkeep
├── src/job_agent/
│   ├── __init__.py
│   ├── __main__.py
│   ├── agent.py
│   ├── cli.py
│   ├── config.py
│   ├── data_loader.py
│   ├── experience.py
│   ├── search.py
│   └── refresh.py
└── tests/
    ├── test_data_loader.py
    ├── test_experience.py
    └── test_search.py
```

## Responsible use
Use this project for learning and personal research. Respect source terms, rate limits, and attribution requirements. Do not bypass logins or access restrictions. Job listings can expire; verify them at the original URL before applying.
