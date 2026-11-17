# Medicare Advantage Plan Index

A searchable web index of all Medicare Advantage health insurance organizations in the United States, built on public CMS data.

**Live site:** https://kellytaylor-adhoc.github.io/kelly-taylor-test/

![React](https://img.shields.io/badge/React-18-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![Data](https://img.shields.io/badge/Data-CMS.gov-lightblue)

## Features

- **312 organizations, 922 contracts** sourced from CMS monthly enrollment files
- Search by company name, marketing name, or CMS contract ID
- Filter by state served and plan type (HMO, PPO, PFFS, etc.)
- Sort by enrollment, number of states, or contract count
- Detail panel per organization: all contracts, states served, plan types, and enrollment figures
- Data refreshes by re-running a single script — no manual data entry

## Data Source

All data is pulled from the [CMS Medicare Advantage & Part D Contract and Enrollment Data](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-advantagepart-d-contract-and-enrollment-data) public files — no API key required.

Two files are used:

| File | Purpose |
|---|---|
| Monthly Enrollment by Contract | Organization names, parent companies, plan types, enrollment |
| Monthly Enrollment by Contract/Plan/State/County (CPSC) | States served per contract |

## Project Structure

```
├── backend/
│   ├── data_fetcher.py   # Downloads and processes CMS data → data/companies.json
│   ├── main.py           # FastAPI server
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx               # Main app: search, filter, sort logic
    │   ├── App.css
    │   └── components/
    │       └── CompanyDetail.jsx # Slide-in detail panel
    ├── index.html
    ├── package.json
    └── vite.config.js            # Proxies /api → localhost:8000
```

## Setup

### 1. Backend

```bash
cd backend
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### 2. Fetch CMS data

Downloads ~50 MB from CMS.gov and produces `backend/data/companies.json`.

```bash
venv/bin/python data_fetcher.py
```

Re-run monthly to pick up the latest CMS enrollment data.

### 3. Start the API server

```bash
venv/bin/uvicorn main:app --reload
# → http://localhost:8000
```

### 4. Frontend

The frontend uses the generated JSON as a static file. Copy it into the frontend
before starting the development server:

```bash
cd frontend
mkdir -p public
cp ../backend/data/companies.json public/companies.json
npm install
npm run dev
# → http://localhost:5173
```

The API server is optional for normal frontend use; the React app reads
`public/companies.json` directly. The API endpoints remain available for local
development or integrations.

## Deploy

From the repository root:

```bash
cd frontend
npm install
npm run deploy
```

The deployment script copies the generated CMS data into `public/`, builds the
Vite app, and publishes the `dist` directory to GitHub Pages.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/companies` | List organizations. Params: `search`, `state`, `plan_type`, `limit`, `offset` |
| GET | `/api/companies/{id}` | Single organization with all contracts |
| GET | `/api/filters` | Available states, plan types, and org types for filter dropdowns |
| GET | `/api/stats` | Total counts and data currency |

## AI-Assisted Development

This project uses [Ad Hoc's Activate AI](https://github.com/adhocteam/activate) to provide consistent AI guidance across tools (GitHub Copilot, Claude, Cursor, etc.).

### What's included

| Path | Purpose |
|---|---|
| `AGENTS.md` | Project-wide instructions — always active |
| `.github/instructions/general.instructions.md` | Commit conventions, code quality standards |
| `.github/instructions/python.instructions.md` | Backend patterns, FastAPI conventions, data fetcher guidance |
| `.github/instructions/typescript.instructions.md` | Frontend patterns, React/JSX conventions |
| `.github/instructions/security.instructions.md` | Security review checklist |
| `.github/prompts/` | 18 reusable prompts (code review, PR prep, ADRs, accessibility, etc.) |
| `.github/agents/` | Specialized agents (docs, service designer, AI workflow, Terraform) |
| `.github/skills/` | Multi-step workflows (documentation, test runner, PR prep, user stories) |

### Using prompts in VS Code

In GitHub Copilot Chat, type `/` followed by a prompt name:

```
/code-review          # Security and correctness review
/prepare-pull-request # Draft a PR description
/generate-tests       # Write tests for the current file
/create-adr           # Document an architecture decision
/accessibility-check  # WCAG audit of a UI component
```

### Customizing

See [`CUSTOMIZATION.md`](CUSTOMIZATION.md) for guidance on adding new instructions, prompts, or skills tailored to this project.
