import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import FiltersPanel from "../components/FiltersPanel";
import { useCases } from "../hooks/useCases";

export default function CasesPage() {
  const [severity, setSeverity] = useState("");
  const [vendor, setVendor] = useState("");
  const [port, setPort] = useState("");
  const [carrier, setCarrier] = useState("");
  const [keyword, setKeyword] = useState("");
  const [minScore, setMinScore] = useState(0);
  const filters = useMemo(() => ({ severity: severity || undefined, vendor: vendor || undefined, port: port || undefined, carrier: carrier || undefined, keyword: keyword || undefined, min_score: minScore || undefined }), [severity, vendor, port, carrier, keyword, minScore]);
  const { data, isLoading } = useCases(filters);
  return (
    <div className="page">
      <div className="page-top"><div><h2>Analyst Case Queue</h2><p className="muted">Working filters, severity-based triage, and deep case explanations.</p></div></div>
      <FiltersPanel severity={severity} vendor={vendor} port={port} carrier={carrier} keyword={keyword} minScore={minScore} options={data?.filters ?? { severities: [], vendors: [], ports: [], carriers: [] }} onChange={(field, value) => ({ severity: setSeverity, vendor: setVendor, port: setPort, carrier: setCarrier, keyword: setKeyword, minScore: setMinScore } as any)[field](value)} onReset={() => { setSeverity(""); setVendor(""); setPort(""); setCarrier(""); setKeyword(""); setMinScore(0); }} />
      <div className="card"><div className="section-header"><h3>Case Results</h3><p className="muted">{data?.items.length ?? 0} items</p></div>{isLoading ? <div>Loading cases...</div> : <div className="table-wrap"><table className="data-table"><thead><tr><th>Case</th><th>Vendor</th><th>Port</th><th>Severity</th><th>Risk Score</th><th>Predictive %</th><th>Recommendation</th></tr></thead><tbody>{data?.items.map((item) => <motion.tr key={item.case_id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}><td><Link className="table-link" to={`/cases/${item.case_id}`}>{item.case_id}</Link></td><td>{item.vendor}</td><td>{item.port}</td><td><span className={`pill ${item.severity.toLowerCase()}`}>{item.severity}</span></td><td>{item.final_risk_score}</td><td>{(item.escalation_probability * 100).toFixed(1)}%</td><td>{item.recommendation}</td></motion.tr>)}</tbody></table></div>}</div>
      <div className="card"><div className="section-header"><h3>Global Feature Signals</h3><p className="muted">Approximate importance signals from the predictive layer.</p></div><div className="chips">{Object.entries(data?.feature_importances ?? {}).map(([feature, score]) => <span className="chip" key={feature}>{feature}: {(score * 100).toFixed(1)}%</span>)}</div></div>
    </div>
  );
}
