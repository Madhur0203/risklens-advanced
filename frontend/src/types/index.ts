export type DashboardData = {
  kpis: Record<string, number>;
  distribution: { severity: string; count: number }[];
  trend: { created_at: string; avg_risk_score: number }[];
  top_vendors: { vendor: string; avg_risk_score: number }[];
  top_ports: { port: string; avg_risk_score: number }[];
  top_carriers: { carrier: string; avg_risk_score: number }[];
};

export type CaseItem = {
  case_id: string;
  vendor: string;
  carrier: string;
  port: string;
  route: string;
  filing_status: string;
  notes: string;
  amount: number;
  quantity: number;
  delay_days: number;
  document_completeness: number;
  vendor_incident_rate: number;
  route_rarity: number;
  cost_spike: number;
  exception_count: number;
  text_signal_score: number;
  rule_score: number;
  anomaly_score: number;
  predictive_score: number;
  final_risk_score: number;
  severity: string;
  escalation_probability: number;
  recommendation: string;
  reasons: string[];
};

export type CasesResponse = {
  items: CaseItem[];
  filters: {
    severities: string[];
    vendors: string[];
    ports: string[];
    carriers: string[];
  };
  feature_importances: Record<string, number>;
};
