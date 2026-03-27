import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { DashboardData } from "../types";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => (await api.get<DashboardData>("/dashboard")).data
  });
}
