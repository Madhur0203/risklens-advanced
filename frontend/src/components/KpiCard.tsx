import { motion } from "framer-motion";

export default function KpiCard({ label, value, accent = "var(--accent)" }: { label: string; value: string | number; accent?: string }) {
  return (
    <motion.div whileHover={{ y: -4, scale: 1.01 }} className="card kpi-card" style={{ borderColor: accent }}>
      <span className="kpi-label">{label}</span>
      <strong className="kpi-value">{value}</strong>
    </motion.div>
  );
}
