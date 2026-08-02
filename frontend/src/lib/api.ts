import type {
  AnalyticsResponse,
  AuthResponse,
  JobMatchResponse,
  LearningRoadmapResponse,
  Page,
  PredictionHistoryItem,
  ResumeListItem,
  ResumeUploadResponse,
  SalaryPredictionRequest,
  SalaryPredictionResponse,
  SkillGapResponse,
  SkillOut,
  User,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

const ACCESS_TOKEN_KEY = "career_intelligence_access_token";
const REFRESH_TOKEN_KEY = "career_intelligence_refresh_token";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown, message: string) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

export const tokenStore = {
  getAccessToken: () =>
    typeof window !== "undefined"
      ? window.localStorage.getItem(ACCESS_TOKEN_KEY)
      : null,
  getRefreshToken: () =>
    typeof window !== "undefined"
      ? window.localStorage.getItem(REFRESH_TOKEN_KEY)
      : null,
  setTokens(access: string, refresh: string) {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, access);
    window.localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  },
  clear() {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

async function refreshAccessToken(): Promise<string | null> {
  const refresh = tokenStore.getRefreshToken();
  if (!refresh) return null;
  try {
    const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) {
      tokenStore.clear();
      return null;
    }
    const data: { access_token: string; refresh_token: string } =
      await res.json();
    tokenStore.setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    return null;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  isForm?: boolean;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, headers = {}, isForm = false } = options;

  const buildHeaders = (token: string | null): Record<string, string> => {
    const h: Record<string, string> = { ...headers };
    if (token) h["Authorization"] = `Bearer ${token}`;
    if (!isForm && body !== undefined) h["Content-Type"] = "application/json";
    return h;
  };

  const doFetch = (token: string | null) =>
    fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: buildHeaders(token),
      body:
        body === undefined
          ? undefined
          : isForm
            ? (body as FormData)
            : JSON.stringify(body),
    });

  let res = await doFetch(tokenStore.getAccessToken());

  if (res.status === 401 && !path.startsWith("/auth/")) {
    const newToken = await refreshAccessToken();
    if (newToken) res = await doFetch(newToken);
  }

  if (res.status === 204) return undefined as T;

  let payload: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!res.ok) {
    const detail =
      typeof payload === "object" && payload && "detail" in (payload as object)
        ? (payload as { detail: unknown }).detail
        : payload;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => (d as { msg?: string }).msg ?? "").join("; ")
          : `Request failed (${res.status})`;
    throw new ApiError(res.status, detail, message);
  }

  return payload as T;
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: { email, password },
    }),
  signup: (fullName: string, email: string, password: string) =>
    request<AuthResponse>("/auth/signup", {
      method: "POST",
      body: { full_name: fullName, email, password },
    }),
  me: () => request<User>("/auth/me"),
  logout: () => request<{ message: string }>("/auth/logout", { method: "POST" }),

  // Resumes
  uploadResume: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<ResumeUploadResponse>("/resumes/upload", {
      method: "POST",
      body: form,
      isForm: true,
    });
  },
  listResumes: (page = 1, pageSize = 10) =>
    request<Page<ResumeListItem>>(`/resumes?page=${page}&page_size=${pageSize}`),
  getResume: (id: number) => request<ResumeUploadResponse["resume"]>(`/resumes/${id}`),
  deleteResume: (id: number) =>
    request<{ message: string }>(`/resumes/${id}`, { method: "DELETE" }),

  // Predictions
  predict: (input: SalaryPredictionRequest) =>
    request<SalaryPredictionResponse>("/predictions/salary", {
      method: "POST",
      body: input,
    }),
  predictionHistory: (page = 1, pageSize = 20) =>
    request<Page<PredictionHistoryItem>>(
      `/predictions/history?page=${page}&page_size=${pageSize}`,
    ),

  // Skills
  skillGap: (resumeSkills: string[], jobDescription: string) =>
    request<SkillGapResponse>("/skills/gap", {
      method: "POST",
      body: { resume_skills: resumeSkills, job_description: jobDescription },
    }),
  roadmap: (missingSkills: string[], dailyHours = 1) =>
    request<LearningRoadmapResponse>("/skills/recommendations/roadmap", {
      method: "POST",
      body: { missing_skills: missingSkills, daily_hours: dailyHours },
    }),
  skillCatalog: (query = "", limit = 100) =>
    request<SkillOut[]>(`/skills/catalog?query=${encodeURIComponent(query)}&limit=${limit}`),
  listRecommendations: (limit = 50) =>
    request<{ skill_name: string; reason: string; status: string }[]>(
      `/skills/recommendations?limit=${limit}`,
    ),

  // Jobs
  matchJobs: (query: string, topK = 6) =>
    request<JobMatchResponse>(`/jobs/match?top_k=${topK}`, {
      method: "POST",
      body: { query },
    }),
  listJobs: (page = 1, pageSize = 20) =>
    request<Page<{ id: number; title: string; company: string; location: string }>>(
      `/jobs?page=${page}&page_size=${pageSize}`,
    ),

  // Analytics
  analytics: () => request<AnalyticsResponse>("/analytics/dashboard"),
};
