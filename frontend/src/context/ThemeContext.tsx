import { createContext, useContext, useEffect, useMemo, useState } from "react";

type Theme = "dark" | "light";

const ThemeContext = createContext<{ theme: Theme; toggleTheme: () => void }>({ theme: "dark", toggleTheme: () => {} });

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem("risklens-theme");
    return saved === "light" ? "light" : "dark";
  });
  useEffect(() => {
    localStorage.setItem("risklens-theme", theme);
    document.documentElement.dataset.theme = theme;
  }, [theme]);
  const value = useMemo(() => ({ theme, toggleTheme: () => setTheme((prev) => (prev === "dark" ? "light" : "dark")) }), [theme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() { return useContext(ThemeContext); }
