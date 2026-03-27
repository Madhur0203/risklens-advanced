import { motion } from "framer-motion";
export default function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="card chart-card">
      <div className="section-header"><h3>{title}</h3></div>
      {children}
    </motion.section>
  );
}
