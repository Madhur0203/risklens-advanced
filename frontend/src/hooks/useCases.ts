import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { CasesResponse } from "../types";

export type CaseFilters = {
  severity?: string;
  vendor?: string;
  port?: string;
  carrier?: string;
  keyword?: string;
  min_score?: number;
};

export function useCases(filters: CaseFilters) {
  return useQuery({
    queryKey: ["cases", filters],
    queryFn: async () => (await api.get<CasesResponse>("/cases", { params: filters })).data
  });
}
