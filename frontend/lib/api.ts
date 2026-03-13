import axios from "axios";
import { BookConfig, BookConfigListItem, Job, SefariaTextSearchResult, TextEntry } from "./types";

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

// Flatten nested BookConfig -> flat backend payload
function toBackendPayload(config: BookConfig): Record<string, unknown> {
  const { format, texts, name } = config;
  return {
    name,
    texts,
    paperheight: format.paperheight,
    paperwidth: format.paperwidth,
    hebfont: format.hebfont,
    hebboldfont: format.hebboldfont,
    engfont: format.engfont,
    commentfont: format.commentfont,
    top: format.top,
    bottom: format.bottom,
    inner: format.inner,
    outer: format.outer,
    fontsize: format.fontsize,
    spacing: Number(format.spacing),
    engfontsize: parseFloat(format.engfontsize) || 10,
    chapfontsize: parseFloat(format.chapfontsize) || 14,
    newpage: format.newpage,
    layout: format.layout,
    twocolfootnotes: format.twocolfootnotes ? 1 : 0,
    parskip: format.parskip,
    pagenumloc: format.pagenumloc,
    pagenumheb: format.pagenumheb ? 1 : 0,
    headpos: format.headpos,
    evenhead: format.evenhead,
    oddhead: format.oddhead,
    covercolor: format.covercolor.replace("#", ""),
    covertextcolor: format.covertextcolor.replace("#", ""),
    covertype: format.covertype,
    backtext: format.backtext,
    titleheb: format.titleheb,
  };
}

// Backend flat config -> nested BookConfig
function fromBackendConfig(data: Record<string, unknown>): BookConfig {
  return {
    id: data.id as string,
    name: data.name as string,
    createdAt: data.created_at as string,
    updatedAt: data.updated_at as string,
    texts: (data.texts as TextEntry[]) ?? [],
    format: {
      paperheight: (data.paperheight as string) ?? "9in",
      paperwidth: (data.paperwidth as string) ?? "6in",
      hebfont: (data.hebfont as string) ?? "David CLM",
      hebboldfont: (data.hebboldfont as string) ?? "",
      engfont: (data.engfont as string) ?? "Linux Libertine O",
      commentfont: (data.commentfont as string) ?? "",
      top: (data.top as string) ?? "0.75in",
      bottom: (data.bottom as string) ?? "0.75in",
      inner: (data.inner as string) ?? "0.75in",
      outer: (data.outer as string) ?? "0.75in",
      fontsize: Number(data.fontsize) ?? 12,
      spacing: String(data.spacing ?? "1.5"),
      engfontsize: `${data.engfontsize ?? 10}pt`,
      chapfontsize: `${data.chapfontsize ?? 14}pt`,
      parskip: (data.parskip as string) ?? "6pt",
      layout: ((data.layout as string) ?? "") as "" | "twocol",
      twocolfootnotes: Boolean(data.twocolfootnotes),
      newpage: (Number(data.newpage) ?? 0) as 0 | 1,
      pagenumloc: (data.pagenumloc as string) ?? "bottom",
      pagenumheb: Boolean(data.pagenumheb),
      headpos: (data.headpos as string) ?? "center",
      evenhead: (data.evenhead as string) ?? "",
      oddhead: (data.oddhead as string) ?? "",
      covercolor: `#${((data.covercolor as string) ?? "FFFFFF").replace("#", "")}`,
      covertextcolor: `#${((data.covertextcolor as string) ?? "000000").replace("#", "")}`,
      covertype: ((data.covertype as string) ?? "softcover") as "hardcover" | "softcover",
      backtext: (data.backtext as string) ?? "",
      titleheb: (data.titleheb as string) ?? "",
    },
  };
}

// Backend JobResponse -> frontend Job
function fromBackendJob(data: Record<string, unknown>): Job {
  const statusMap: Record<string, Job["status"]> = {
    pending: "pending",
    running: "running",
    success: "completed",
    failure: "failed",
  };
  return {
    id: data.id as string,
    status: statusMap[data.status as string] ?? "pending",
    config: {} as BookConfig,
    createdAt: data.created_at as string,
    completedAt: data.updated_at as string,
    error: data.error_message as string | undefined,
    pdfUrl: data.pdf_path ? `${apiClient.defaults.baseURL}/api/v1/jobs/${data.id}/download` : undefined,
  };
}

export const api = {
  // -- Sefaria text search
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

  // -- Jobs
  createJob: async (config: BookConfig): Promise<Job> => {
    const { data } = await apiClient.post("/api/v1/jobs", toBackendPayload(config));
    return fromBackendJob(data);
  },

  getJob: async (jobId: string): Promise<Job> => {
    const { data } = await apiClient.get(`/api/v1/jobs/${jobId}`);
    return fromBackendJob(data);
  },

  // -- Saved configs
  getConfigs: async (): Promise<BookConfigListItem[]> => {
    const { data } = await apiClient.get("/api/v1/configs");
    return (data as Record<string, unknown>[]).map((item) => ({
      id: item.id as string,
      name: item.name as string,
      description: item.description as string | undefined,
      createdAt: item.created_at as string,
      updatedAt: item.updated_at as string,
    }));
  },

  getConfigById: async (id: string): Promise<BookConfig> => {
    const { data } = await apiClient.get(`/api/v1/configs/${id}`);
    return fromBackendConfig(data);
  },

  createConfig: async (config: BookConfig): Promise<BookConfig> => {
    const { data } = await apiClient.post("/api/v1/configs", toBackendPayload(config));
    return fromBackendConfig(data);
  },

  deleteConfig: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/configs/${id}`);
  },

  downloadPdf: (jobId: string): string => {
    return `${apiClient.defaults.baseURL}/api/v1/jobs/${jobId}/download`;
  },
};

export default apiClient;