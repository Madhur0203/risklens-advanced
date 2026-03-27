import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { CaseItem } from "../types";
import { useState } from "react";

export default function CaseDetailPage() {
  const { caseId } = useParams();
  const qc = useQueryClient();
  const [label, setLabel] = useState("true_positive");
  const [comment, setComment] = useState("");
  const { data, isLoading } = useQuery({ queryKey: ["case", caseId], queryFn: async () => (await api.get<CaseItem>(`/cases/${caseId}`)).data, enabled: !!caseId });
  const feedback = useMutation({ mutationFn: async () => (await api.post("/feedback", { case_id: caseId, analyst_label: label, analyst_comment: comment })).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["case", caseId] }); setComment(""); } });
  if (isLoading || !data) return <div className="page"><div className="card">Loading case...</div></div>;
  return (
    <div className="page">
      <div className="page-top"><div><h2>{data.case_id}</h2><p className="muted">{data.vendor} · {data.carrier} · {data.port} · {data.route}</p></div><span className={`pill ${data.severity.toLowerCase()}`}>{data.severity}</span></div>
      <div className="detail-grid">
        <div className="card"><h3>Risk Composition</h3><div className="metric-list"><div><span>Rule Score</span><strong>{data.rule_score}</strong></div><div><span>Anomaly Score</span><strong>{data.anomaly_score}</strong></div><div><span>Predictive Score</span><strong>{data.predictive_score}</strong></div><div><span>Text Signal Score</span><strong>{data.text_signal_score}</strong></div><div><span>Final Risk Score</span><strong>{data.final_risk_score}</strong></div><div><span>Escalation Probability</span><strong>{(data.escalation_probability * 100).toFixed(1)}%</strong></div></div></div>
        <div className="card"><h3>Why this case was flagged</h3><ul className="reason-list">{data.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul><h4>Recommendation</h4><p>{data.recommendation}</p><h4>Notes</h4><p>{data.notes}</p></div>
      </div>
      <div className="card"><div className="section-header"><h3>Analyst Feedback Loop</h3><button className="primary-btn" onClick={() => feedback.mutate()}>{feedback.isPending ? "Saving..." : "Submit Feedback"}</button></div><div className="feedback-form"><select value={label} onChange={(e) => setLabel(e.target.value)}><option value="true_positive">True Positive</option><option value="false_positive">False Positive</option><option value="monitor">Monitor</option></select><textarea value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Analyst comment" rows={5} /></div></div>
    </div>
  );
}
