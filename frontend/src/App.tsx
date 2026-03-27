import { NavLink, Route, Routes } from "react-router-dom";
import { motion } from "framer-motion";
import DashboardPage from "./pages/DashboardPage";
import CasesPage from "./pages/CasesPage";
import UploadPage from "./pages/UploadPage";
import CaseDetailPage from "./pages/CaseDetailPage";
import { useTheme } from "./context/ThemeContext";

function App() {
  const { theme, toggleTheme } = useTheme();
  return (
    <div className={`app-shell ${theme}`}>
      <aside className="sidebar">
        <motion.div initial={{ opacity: 0, y: -14 }} animate={{ opacity: 1, y: 0 }} className="brand">
          <div className="brand-badge">RL</div>
          <div>
            <h1>RiskLens</h1>
            <p>Signal Intelligence Platform</p>
          </div>
        </motion.div>
        <nav className="nav">
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/cases">Cases</NavLink>
          <NavLink to="/upload">Upload</NavLink>
        </nav>
        <button className="theme-btn" onClick={toggleTheme}>Toggle {theme === "dark" ? "Light" : "Dark"} Theme</button>
      </aside>
      <main className="content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/cases" element={<CasesPage />} />
          <Route path="/cases/:caseId" element={<CaseDetailPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
