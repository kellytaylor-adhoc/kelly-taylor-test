export default function CompanyDetail({ company, onClose }) {
  if (!company) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header" style={{ position: "relative" }}>
          <h2>{company.parent_org}</h2>
          <p>Medicare Advantage Organization</p>
          <button className="modal-close" onClick={onClose} aria-label="Close">×</button>
        </div>

        <div className="modal-body">
          <div className="stat-grid">
            <div className="stat-card">
              <div className="num">{company.contract_count}</div>
              <div className="lbl">Contracts</div>
            </div>
            <div className="stat-card">
              <div className="num">{company.states.length}</div>
              <div className="lbl">States</div>
            </div>
            <div className="stat-card">
              <div className="num">{company.total_enrollment > 0 ? formatEnrollment(company.total_enrollment) : "—"}</div>
              <div className="lbl">Enrollees</div>
            </div>
          </div>

          <div className="detail-section">
            <h3>Plan Types</h3>
            <div className="states-wrap">
              {company.plan_types.map((pt) => (
                <span key={pt} className="tag tag-blue">{pt}</span>
              ))}
            </div>
          </div>

          {company.states.length > 0 && (
            <div className="detail-section">
              <h3>States Served ({company.states.length})</h3>
              <div className="states-wrap">
                {company.states.map((s) => (
                  <span key={s} className="tag tag-gray">{s}</span>
                ))}
              </div>
            </div>
          )}

          <div className="detail-section">
            <h3>Contracts ({company.contract_count})</h3>
            {company.contracts.map((ct) => (
              <div key={ct.contract_id} className="contract-card">
                <div className="cid">{ct.contract_id}</div>
                <div className="cname">{ct.marketing_name || ct.org_name}</div>
                {ct.marketing_name && ct.marketing_name !== ct.org_name && (
                  <div className="cmeta">{ct.org_name}</div>
                )}
                <div className="cmeta">
                  {ct.plan_type} · {ct.org_type}
                  {ct.offers_part_d && " · Includes Part D"}
                </div>
                {ct.enrollment > 0 && (
                  <div className="cmeta">{ct.enrollment.toLocaleString()} enrollees</div>
                )}
                {ct.states.length > 0 && (
                  <div className="contract-states">
                    {ct.states.map((s) => (
                      <span key={s} className="tag tag-gray">{s}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function formatEnrollment(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(0) + "K";
  return n.toLocaleString();
}
