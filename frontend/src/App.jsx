import { useEffect, useMemo, useRef, useState } from "react";
import CompanyDetail from "./components/CompanyDetail.jsx";

const SORT_KEYS = {
  name: (c) => c.parent_org.toLowerCase(),
  contracts: (c) => c.contract_count,
  states: (c) => c.states.length,
  enrollment: (c) => c.total_enrollment,
};

export default function App() {
  const [allCompanies, setAllCompanies] = useState([]);
  const [filters, setFilters] = useState({ states: [], plan_types: [] });
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [search, setSearch] = useState("");
  const [stateFilter, setStateFilter] = useState("");
  const [planFilter, setPlanFilter] = useState("");
  const [sortKey, setSortKey] = useState("enrollment");
  const [sortAsc, setSortAsc] = useState(false);
  const [selected, setSelected] = useState(null);

  const searchTimer = useRef(null);
  const [debouncedSearch, setDebouncedSearch] = useState("");

  useEffect(() => {
    clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(() => setDebouncedSearch(search), 250);
    return () => clearTimeout(searchTimer.current);
  }, [search]);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}companies.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        const companies = data.companies || [];
        setAllCompanies(companies);
        setFilters({
          states: [...new Set(companies.flatMap((c) => c.states))].sort(),
          plan_types: [...new Set(companies.flatMap((c) => c.plan_types))].sort(),
        });
        setStats({
          total_companies: data.total_companies,
          total_contracts: data.total_contracts,
          data_period: data.data_period,
          data_loaded: companies.length > 0,
        });
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const displayed = useMemo(() => {
    let list = allCompanies;

    if (debouncedSearch) {
      const q = debouncedSearch.toLowerCase();
      list = list.filter(
        (c) =>
          c.parent_org.toLowerCase().includes(q) ||
          c.contracts.some(
            (ct) =>
              ct.org_name.toLowerCase().includes(q) ||
              ct.marketing_name.toLowerCase().includes(q) ||
              ct.contract_id.toLowerCase().includes(q)
          )
      );
    }

    if (stateFilter) {
      list = list.filter((c) => c.states.includes(stateFilter));
    }

    if (planFilter) {
      list = list.filter((c) => c.plan_types.includes(planFilter));
    }

    const keyFn = SORT_KEYS[sortKey];
    list = [...list].sort((a, b) => {
      const av = keyFn(a);
      const bv = keyFn(b);
      if (av < bv) return sortAsc ? -1 : 1;
      if (av > bv) return sortAsc ? 1 : -1;
      return 0;
    });

    return list;
  }, [allCompanies, debouncedSearch, stateFilter, planFilter, sortKey, sortAsc]);

  function handleSort(key) {
    if (sortKey === key) setSortAsc((a) => !a);
    else { setSortKey(key); setSortAsc(key === "name"); }
  }

  function clearFilters() {
    setSearch("");
    setStateFilter("");
    setPlanFilter("");
  }

  const hasFilters = search || stateFilter || planFilter;

  return (
    <>
      <header className="header">
        <h1>Medicare Advantage Plan Index</h1>
        <div className="header-meta">
          {stats?.data_loaded
            ? `${stats.total_companies.toLocaleString()} organizations · ${stats.total_contracts.toLocaleString()} contracts · CMS data: ${stats.data_period}`
            : "No data loaded — run the data fetcher to populate"}
        </div>
      </header>

      <div className="controls">
        <input
          className="search-input"
          type="search"
          placeholder="Search by company name, marketing name, or contract ID…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="filter-select"
          value={stateFilter}
          onChange={(e) => setStateFilter(e.target.value)}
        >
          <option value="">All states</option>
          {filters.states.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select
          className="filter-select"
          value={planFilter}
          onChange={(e) => setPlanFilter(e.target.value)}
        >
          <option value="">All plan types</option>
          {filters.plan_types.map((pt) => (
            <option key={pt} value={pt}>{pt}</option>
          ))}
        </select>
        {hasFilters && (
          <button className="clear-btn" onClick={clearFilters}>Clear filters</button>
        )}
      </div>

      <main className="main">
        {loading && (
          <div className="state-box">
            <div className="spinner" />
            <p>Loading…</p>
          </div>
        )}

        {error && (
          <div className="state-box">
            <h3>Could not load data</h3>
            <p>Run the data fetcher to generate the index, then refresh.</p>
            <code>python backend/data_fetcher.py</code>
          </div>
        )}

        {!loading && !error && (
          <>
            <div className="results-bar">
              <span>
                {displayed.length === allCompanies.length
                  ? `${displayed.length.toLocaleString()} organizations`
                  : `${displayed.length.toLocaleString()} of ${allCompanies.length.toLocaleString()} organizations`}
              </span>
              {!stats?.data_loaded && (
                <span style={{ color: "#c00" }}>
                  Data not loaded — run: <code>python backend/data_fetcher.py</code>
                </span>
              )}
            </div>

            {displayed.length === 0 ? (
              <div className="state-box">
                <h3>No results</h3>
                <p>Try adjusting your search or filters.</p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <SortHeader label="Organization" k="name" sortKey={sortKey} sortAsc={sortAsc} onSort={handleSort} />
                      <SortHeader label="Contracts" k="contracts" sortKey={sortKey} sortAsc={sortAsc} onSort={handleSort} />
                      <SortHeader label="States" k="states" sortKey={sortKey} sortAsc={sortAsc} onSort={handleSort} />
                      <th>Plan Types</th>
                      <SortHeader label="Enrollment" k="enrollment" sortKey={sortKey} sortAsc={sortAsc} onSort={handleSort} />
                    </tr>
                  </thead>
                  <tbody>
                    {displayed.map((c) => (
                      <tr key={c.id} onClick={() => setSelected(c)}>
                        <td>
                          <div className="company-name">{c.parent_org}</div>
                          {c.contracts[0]?.marketing_name &&
                            c.contracts[0].marketing_name !== c.parent_org && (
                              <div className="company-contracts">
                                a.k.a. {c.contracts[0].marketing_name}
                              </div>
                            )}
                        </td>
                        <td>{c.contract_count}</td>
                        <td>{c.states.length > 0 ? c.states.length : "—"}</td>
                        <td>
                          {c.plan_types.slice(0, 3).map((pt) => (
                            <span key={pt} className="tag tag-blue">{pt}</span>
                          ))}
                          {c.plan_types.length > 3 && (
                            <span className="tag tag-gray">+{c.plan_types.length - 3}</span>
                          )}
                        </td>
                        <td className="enrollment-num">
                          {c.total_enrollment > 0
                            ? c.total_enrollment.toLocaleString()
                            : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </main>

      {selected && (
        <CompanyDetail company={selected} onClose={() => setSelected(null)} />
      )}
    </>
  );
}

function SortHeader({ label, k, sortKey, sortAsc, onSort }) {
  const active = sortKey === k;
  return (
    <th onClick={() => onSort(k)}>
      {label}
      <span className={`sort-icon ${active ? "active" : ""}`}>
        {active ? (sortAsc ? " ▲" : " ▼") : " ↕"}
      </span>
    </th>
  );
}
