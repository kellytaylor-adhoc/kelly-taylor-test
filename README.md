# Medicare Advantage Plan Index

A searchable web index of all Medicare Advantage health insurance organizations in the United States, built on public CMS data.

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

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/companies` | List organizations. Params: `search`, `state`, `plan_type`, `limit`, `offset` |
| GET | `/api/companies/{id}` | Single organization with all contracts |
| GET | `/api/filters` | Available states, plan types, and org types for filter dropdowns |
| GET | `/api/stats` | Total counts and data currency |
