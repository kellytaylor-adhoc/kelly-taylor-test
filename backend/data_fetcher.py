"""
Downloads and processes CMS Medicare Advantage data from public files.
Run this script to populate backend/data/companies.json.
"""

import csv
import io
import json
import re
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

import requests

DATA_DIR = Path(__file__).parent / "data"

# SSA state code -> 2-letter abbreviation
SSA_TO_ABBR = {
    "01": "AL", "02": "AK", "03": "AZ", "04": "AR", "05": "CA",
    "06": "CO", "07": "CT", "08": "DE", "09": "DC", "10": "FL",
    "11": "GA", "12": "HI", "13": "ID", "14": "IL", "15": "IN",
    "16": "IA", "17": "KS", "18": "KY", "19": "LA", "20": "ME",
    "21": "MD", "22": "MA", "23": "MI", "24": "MN", "25": "MS",
    "26": "MO", "27": "MT", "28": "NE", "29": "NV", "30": "NH",
    "31": "NJ", "32": "NM", "33": "NY", "34": "NC", "35": "ND",
    "36": "OH", "37": "OK", "38": "OR", "39": "PA", "40": "RI",
    "41": "SC", "42": "SD", "43": "TN", "44": "TX", "45": "UT",
    "46": "VT", "47": "VA", "48": "WA", "49": "WV", "50": "WI",
    "51": "WY", "52": "PR", "53": "VI", "54": "GU", "55": "MP", "56": "AS",
}

# Org types that represent Medicare Advantage (exclude standalone PDPs)
MA_ORG_TYPES = {
    "Local CCP",
    "Regional CCP",
    "MSA",
    "PFFS",
    "RFB-PFFS",
    "Demonstrations",
    "National PACE",
    "1876 Cost",
    "HCPP - 1833 Cost",
}

MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]


def candidate_months(n=6):
    """Return (month_name, year) tuples for the last n months."""
    now = datetime.now()
    for i in range(1, n + 1):  # start 1 month back since current month rarely published yet
        d = now - timedelta(days=30 * i)
        yield MONTHS[d.month - 1], d.year


def download_zip(url: str) -> bytes | None:
    print(f"  GET {url}")
    try:
        resp = requests.get(url, timeout=120)
        if resp.status_code == 200:
            return resp.content
        print(f"  -> HTTP {resp.status_code}")
    except requests.RequestException as e:
        print(f"  -> Error: {e}")
    return None


def read_csv_from_zip(data: bytes, prefer_name: str | None = None) -> tuple[list[str], list[dict]] | None:
    """Extract a CSV from a ZIP and return (headers, rows)."""
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv") and not n.startswith("__")]
        if not csv_names:
            return None
        # Prefer a specific filename pattern if requested
        if prefer_name:
            match = next((n for n in csv_names if prefer_name.lower() in n.lower()), None)
            chosen = match or csv_names[0]
        else:
            chosen = csv_names[0]
        with zf.open(chosen) as f:
            content = f.read().decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        return reader.fieldnames, rows


def parse_enrollment(value: str) -> int:
    value = value.strip()
    if value in ("*", "", "N/A"):
        return 0
    try:
        return int(value.replace(",", ""))
    except ValueError:
        return 0


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch_contract_data() -> dict | None:
    """Download monthly contract enrollment file. Returns {contract_id: contract_dict}."""
    for month, year in candidate_months():
        url = f"https://www.cms.gov/files/zip/monthly-enrollment-contract-{month}-{year}.zip"
        data = download_zip(url)
        if data is None:
            continue
        result = read_csv_from_zip(data)
        if result is None:
            continue
        headers, rows = result
        print(f"  Parsed {len(rows)} rows from {month} {year} contract file")
        print(f"  Columns: {headers[:8]}")

        contracts = {}
        for row in rows:
            org_type = row.get("Organization Type", "").strip()
            if org_type not in MA_ORG_TYPES:
                continue
            contract_id = row.get("Contract Number", "").strip()
            if not contract_id:
                continue
            parent = row.get("Parent Organization", "").strip()
            org_name = row.get("Organization Name", "").strip()
            contracts[contract_id] = {
                "contract_id": contract_id,
                "org_name": org_name,
                "marketing_name": row.get("Organization Marketing Name", "").strip(),
                "parent_org": parent or org_name,
                "plan_type": row.get("Plan Type", "").strip(),
                "org_type": org_type,
                "offers_part_d": row.get("Offers Part D", "").strip().lower() == "yes",
                "enrollment": parse_enrollment(row.get("Enrollment", "0")),
                "states": [],
            }
        print(f"  Found {len(contracts)} MA contracts")
        return contracts, f"{month.title()} {year}"

    return None, None


def fetch_state_data(contract_ids: set, month: str, year: int) -> dict:
    """Download CPSC file and return {contract_id: [state_abbr, ...]}."""
    url = f"https://www.cms.gov/files/zip/monthly-enrollment-cpsc-{month}-{year}.zip"
    data = download_zip(url)
    if data is None:
        return {}

    # The CPSC ZIP has two CSVs; we need the Enrollment_Info one (has State column)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        chosen = next((n for n in csv_names if "enrollment_info" in n.lower()), None) or (csv_names[0] if csv_names else None)
        if not chosen:
            return {}
        print(f"  Using: {chosen}")
        with zf.open(chosen) as f:
            content = f.read().decode("utf-8-sig", errors="replace")

    contract_states: dict[str, set] = {cid: set() for cid in contract_ids}
    reader = csv.DictReader(io.StringIO(content))
    headers = reader.fieldnames or []
    print(f"  Columns: {headers}")

    contract_col = next((h for h in headers if "contract" in h.lower() and ("number" in h.lower() or "id" in h.lower())), "Contract Number")
    state_col = next((h for h in headers if h.strip().lower() == "state"), None)
    ssa_col = next((h for h in headers if "ssa state" in h.lower()), None)

    row_count = 0
    for row in reader:
        row_count += 1
        cid = row.get(contract_col, "").strip()
        if cid not in contract_states:
            continue

        # Try the State column first (2-letter abbreviation)
        if state_col:
            val = row.get(state_col, "").strip()
            if len(val) == 2 and val.isalpha():
                contract_states[cid].add(val.upper())
                continue

        # Fall back to SSA State County Code (first 2 digits = SSA state code)
        if ssa_col:
            ssa = row.get(ssa_col, "").strip()
            if len(ssa) >= 2:
                abbr = SSA_TO_ABBR.get(ssa[:2])
                if abbr:
                    contract_states[cid].add(abbr)

    print(f"  Processed {row_count:,} enrollment rows")
    return {cid: sorted(states) for cid, states in contract_states.items()}


def build_company_index(contracts: dict, state_map: dict) -> list:
    # Attach states to each contract
    for cid, contract in contracts.items():
        contract["states"] = state_map.get(cid, [])

    # Group by parent org
    by_parent: dict[str, list] = {}
    for contract in contracts.values():
        key = contract["parent_org"]
        by_parent.setdefault(key, []).append(contract)

    companies = []
    for parent_org, org_contracts in by_parent.items():
        all_states = sorted({s for c in org_contracts for s in c["states"]})
        plan_types = sorted({c["plan_type"] for c in org_contracts if c["plan_type"]})
        total_enrollment = sum(c["enrollment"] for c in org_contracts)
        companies.append({
            "id": slugify(parent_org),
            "parent_org": parent_org,
            "contracts": sorted(org_contracts, key=lambda c: c["contract_id"]),
            "states": all_states,
            "plan_types": plan_types,
            "total_enrollment": total_enrollment,
            "contract_count": len(org_contracts),
        })

    # Sort by enrollment descending
    companies.sort(key=lambda c: c["total_enrollment"], reverse=True)
    return companies


def main():
    DATA_DIR.mkdir(exist_ok=True)

    print("Step 1: Fetching contract data...")
    contracts, data_period = fetch_contract_data()
    if not contracts:
        print("ERROR: Could not download contract data. Check your internet connection.")
        return

    # Determine which month/year we got data for (reparse from data_period string)
    parts = data_period.lower().split()
    month_name, year = parts[0], int(parts[1])

    print(f"\nStep 2: Fetching state data ({data_period})...")
    state_map = fetch_state_data(set(contracts.keys()), month_name, year)
    if not state_map:
        print("  Warning: Could not load state data. States will be empty.")

    print("\nStep 3: Building company index...")
    companies = build_company_index(contracts, state_map)
    print(f"  {len(companies)} unique organizations")

    output = {
        "data_period": data_period,
        "generated_at": datetime.now().isoformat(),
        "total_companies": len(companies),
        "total_contracts": sum(c["contract_count"] for c in companies),
        "companies": companies,
    }

    out_path = DATA_DIR / "companies.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nDone! Saved to {out_path}")
    print(f"  {output['total_companies']} companies, {output['total_contracts']} contracts")


if __name__ == "__main__":
    main()
