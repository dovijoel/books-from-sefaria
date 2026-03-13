import axios from "axios";
import { BookConfig, Job, SefariaTextSearchResult } from "./types";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);

export const api = {
  // ── Sefaria text search ─────────────────────────────────────────────────
  searchTexts: async (query: string): Promise<SefariaTextSearchResult[]> => {
    const { data } = await apiClient.get("/api/v1/sefaria/search", {
      params: { q: query },
    });
    return data;
  },

  getTextInfo: async (ref: string): Promise<Record<string, unknown>> => {
    const { data } = await apiClient.get(
      `/api/v1/sefaria/text/${encodeURIComponent(ref)}`
    );
    return data;
  },

  // ── Jobs ────────────────────────────────────────────────────────────────
  createJob: async (config: BookConfig): Promise<{ job_id: string }> => {
    const { data } = await apiClient.post("/api/v1/jobs", { config });
    return data;
  },

  getJob: async (jobId: string): Promise<Job> => {
    const { data } = await apiClient.get(`/api/v1/jobs/${jobId}`);
    return data;
  },

  // ── Saved configs ───────────────────────────────────────────────────────
  getConfigs: async (): Promise<BookConfig[]> => {
    const { data } = await apiClient.get("/api/v1/configs");
    return data;
  },

  createConfig: async (config: BookConfig): Promise<BookConfig> => {
    const { data } = await apiClient.post("/api/v1/configs", config);
    return data;
  },

  deleteConfig: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/configs/${id}`);
  },
};

export default apiClient;
