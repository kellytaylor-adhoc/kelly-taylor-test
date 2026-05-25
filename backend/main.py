from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="Medicare Advantage Index API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).parent / "data" / "companies.json"


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {"companies": [], "total_companies": 0, "total_contracts": 0, "data_period": None, "generated_at": None}
    with open(DATA_FILE) as f:
        return json.load(f)


@app.get("/api/stats")
def get_stats():
    d = load_data()
    return {
        "total_companies": d["total_companies"],
        "total_contracts": d["total_contracts"],
        "data_period": d.get("data_period"),
        "generated_at": d.get("generated_at"),
        "data_loaded": DATA_FILE.exists(),
    }


@app.get("/api/filters")
def get_filters():
    companies = load_data()["companies"]
    states = sorted({s for c in companies for s in c["states"]})
    plan_types = sorted({pt for c in companies for pt in c["plan_types"]})
    org_types = sorted({ct["org_type"] for c in companies for ct in c["contracts"]})
    return {"states": states, "plan_types": plan_types, "org_types": org_types}


@app.get("/api/companies")
def list_companies(
    search: Optional[str] = None,
    state: Optional[str] = None,
    plan_type: Optional[str] = None,
    limit: int = Query(default=500, le=1000),
    offset: int = 0,
):
    companies = load_data()["companies"]

    if search:
        q = search.lower()
        companies = [
            c for c in companies
            if q in c["parent_org"].lower()
            or any(
                q in ct["org_name"].lower() or q in ct.get("marketing_name", "").lower()
                for ct in c["contracts"]
            )
        ]

    if state:
        state = state.upper()
        companies = [c for c in companies if state in c["states"]]

    if plan_type:
        companies = [c for c in companies if plan_type in c["plan_types"]]

    total = len(companies)
    page = companies[offset: offset + limit]

    return {"total": total, "offset": offset, "limit": limit, "companies": page}


@app.get("/api/companies/{company_id}")
def get_company(company_id: str):
    companies = load_data()["companies"]
    for c in companies:
        if c["id"] == company_id:
            return c
    raise HTTPException(status_code=404, detail="Company not found")
