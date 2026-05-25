---
description: 'Python conventions and project-specific patterns'
applyTo: '**/*.py'
excludeAgent: []
---
# Python Instructions

Project-specific Python guidance for the Medicare Advantage Index backend.

## Version and Runtime

- **Python version**: 3.12+
- **Package manager**: pip
- **Virtual environment**: `venv` — always at `backend/venv/`; activate with `source backend/venv/bin/activate`

## Tooling

| Tool | Command | Purpose |
|------|---------|---------|
| Run server | `venv/bin/uvicorn main:app --reload` | Start FastAPI dev server on port 8000 |
| Fetch data | `venv/bin/python data_fetcher.py` | Download and rebuild CMS data |
| Install deps | `venv/bin/pip install -r requirements.txt` | Install/update dependencies |

No linter or formatter is currently configured. When adding one, prefer `ruff` (covers both formatting and linting).

## Project Structure

```text
backend/
├── main.py           # FastAPI app — API routes only, no business logic
├── data_fetcher.py   # Standalone script: downloads CMS ZIPs, produces data/companies.json
├── requirements.txt  # Pinned dependencies
└── data/
    └── companies.json  # Generated output — gitignored, never edit by hand
```

## Team Conventions

### Preferred Patterns

- Use `pathlib.Path` over `os.path` for all file operations
- Use `requests` for HTTP (already a dependency); do not add `httpx` without discussion
- Use `io.BytesIO` + `zipfile.ZipFile` for in-memory ZIP handling (established pattern in `data_fetcher.py`)
- Use `csv.DictReader` for CSV parsing — never parse CSV by splitting strings
- Use `X | None` union syntax (Python 3.10+) instead of `Optional[X]`

### Patterns to Avoid

- Do not use `eval()` or `exec()`
- Avoid bare `except:` — always specify exception types (e.g., `except requests.RequestException`)
- Do not edit `data/companies.json` by hand — it is a generated artifact; modify `data_fetcher.py` instead
- Do not add new top-level scripts; extend `data_fetcher.py` or `main.py` as appropriate

## FastAPI Conventions

- All routes live in `main.py`; keep route handlers thin
- Use `Query(default=..., le=...)` for validated query parameters
- Raise `HTTPException` with meaningful status codes for errors
- CORS is locked to `localhost:5173` and `localhost:4173` — do not broaden without review

## Data Fetcher Conventions

- The fetcher is a standalone CLI script (`if __name__ == "__main__"`)
- It tries the last 6 months of CMS data in descending order and uses the first that returns HTTP 200
- After regenerating `data/companies.json`, also copy it to `../frontend/public/companies.json` for the static build

## Dependencies

- Pin all dependencies in `requirements.txt` with exact versions
- Current dependencies: `fastapi`, `uvicorn[standard]`, `requests`
- Prefer stdlib solutions over adding new packages
