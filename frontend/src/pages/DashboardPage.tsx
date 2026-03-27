import { useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { BarChart, Bar, CartesianGrid, Legend, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api/client";
import { useDashboard } from "../hooks/useDashboard";
import KpiCard from "../components/KpiCard";
import ChartCard from "../components/ChartCard";

const pieColors = ["#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"];

export default function DashboardPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useDashboard();
  const bootstrap = useMutation({
    mutationFn: async () => (await api.post("/bootstrap")).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["cases"] });
    }
  });

  return (
    <div className="page">
      <div className="page-top">
        <div>
          <h2>Executive Risk View</h2>
          <p className="muted">Hybrid detection across rules, anomaly signals, prediction, and text intelligence.</p>
        </div>
        <button className="primary-btn" onClick={() => bootstrap.mutate()}>{bootstrap.isPending ? "Bootstrapping..." : "Generate Sample Intelligence Dataset"}</button>
      </div>
      {isLoading || !data ? <div className="card">Loading dashboard...</div> : <>
        <motion.div className="kpi-grid" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <KpiCard label="Total Cases" value={data.kpis.total_cases} />
          <KpiCard label="Avg Risk Score" value={data.kpis.avg_risk_score} accent="#f59e0b" />
          <KpiCard label="Critical Cases" value={data.kpis.critical_cases} accent="#ef4444" />
          <KpiCard label="High Cases" value={data.kpis.high_cases} accent="#8b5cf6" />
          <KpiCard label="Avg Escalation %" value={`${data.kpis.avg_escalation_probability}%`} accent="#06b6d4" />
        </motion.div>
        <div className="chart-grid two-up">
          <ChartCard title="Risk Trend Over Time">
            <ResponsiveContainer width="100%" height={320}><LineChart data={data.trend}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="created_at" hide /><YAxis /><Tooltip /><Legend /><Line type="monotone" dataKey="avg_risk_score" stroke="#3b82f6" strokeWidth={3} dot={false} /></LineChart></ResponsiveContainer>
          </ChartCard>
          <ChartCard title="Severity Distribution">
            <ResponsiveContainer width="100%" height={320}><PieChart><Pie data={data.distribution} dataKey="count" nameKey="severity" outerRadius={110} label>{data.distribution.map((_, index) => <Cell key={index} fill={pieColors[index % pieColors.length]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer>
          </ChartCard>
        </div>
        <div className="chart-grid two-up">
          <ChartCard title="Top Risk Vendors">
            <ResponsiveContainer width="100%" height={320}><BarChart data={data.top_vendors}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="vendor" hide /><YAxis /><Tooltip /><Bar dataKey="avg_risk_score" fill="#ef4444" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer>
          </ChartCard>
          <ChartCard title="Port Risk Comparison">
            <ResponsiveContainer width="100%" height={320}><BarChart data={data.top_ports}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="port" /><YAxis /><Tooltip /><Bar dataKey="avg_risk_score" fill="#8b5cf6" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer>
          </ChartCard>
        </div>
      </>}
    </div>
  );
}
