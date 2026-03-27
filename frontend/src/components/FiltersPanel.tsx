type Props = {
  severity: string;
  vendor: string;
  port: string;
  carrier: string;
  keyword: string;
  minScore: number;
  options: { severities: string[]; vendors: string[]; ports: string[]; carriers: string[] };
  onChange: (field: string, value: string | number) => void;
  onReset: () => void;
};

export default function FiltersPanel(props: Props) {
  const { severity, vendor, port, carrier, keyword, minScore, options, onChange, onReset } = props;
  return (
    <div className="card filter-panel">
      <div className="section-header"><h3>Filters</h3><button className="ghost-btn" onClick={onReset}>Reset</button></div>
      <div className="filters-grid">
        <select value={severity} onChange={(e) => onChange("severity", e.target.value)}><option value="">All Severities</option>{options.severities.map((v) => <option key={v} value={v}>{v}</option>)}</select>
        <select value={vendor} onChange={(e) => onChange("vendor", e.target.value)}><option value="">All Vendors</option>{options.vendors.map((v) => <option key={v} value={v}>{v}</option>)}</select>
        <select value={port} onChange={(e) => onChange("port", e.target.value)}><option value="">All Ports</option>{options.ports.map((v) => <option key={v} value={v}>{v}</option>)}</select>
        <select value={carrier} onChange={(e) => onChange("carrier", e.target.value)}><option value="">All Carriers</option>{options.carriers.map((v) => <option key={v} value={v}>{v}</option>)}</select>
        <input value={keyword} placeholder="Text keyword" onChange={(e) => onChange("keyword", e.target.value)} />
        <input type="range" min={0} max={100} step={1} value={minScore} onChange={(e) => onChange("minScore", Number(e.target.value))} />
      </div>
      <p className="muted">Minimum risk score: <strong>{minScore}</strong></p>
    </div>
  );
}
