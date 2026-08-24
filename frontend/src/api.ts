import type {
  Assessment,
  AssuranceItem,
  AuditEntry,
  Review,
  Summary,
} from "./types";

const API = "/api";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  init: RequestInit & { actor?: string } = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (init.actor) {
    headers.set("X-Actor", init.actor);
  }
  const response = await fetch(`${API}${path}`, { ...init, headers });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ? JSON.stringify(body.detail) : detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(response.status, detail);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; data_boundary: string }>("/health"),
  summary: () => request<Summary>("/summary"),
  listAssessments: (status?: string) =>
    request<Assessment[]>(status ? `/assessments?status=${encodeURIComponent(status)}` : "/assessments"),
  getAssessment: (id: number) => request<Assessment>(`/assessments/${id}`),
  createAssessment: (body: Record<string, string>, actor: string) =>
    request<Assessment>("/assessments", { method: "POST", body: JSON.stringify(body), actor }),
  listItems: (id: number) => request<AssuranceItem[]>(`/assessments/${id}/items`),
  addItem: (id: number, body: Record<string, string>, actor: string) =>
    request<AssuranceItem>(`/assessments/${id}/items`, {
      method: "POST",
      body: JSON.stringify(body),
      actor,
    }),
  listReviews: (id: number) => request<Review[]>(`/assessments/${id}/reviews`),
  addReview: (id: number, body: Record<string, string>, actor: string) =>
    request<Review>(`/assessments/${id}/reviews`, {
      method: "POST",
      body: JSON.stringify(body),
      actor,
    }),
  auditLog: (assessmentId?: number) =>
    request<AuditEntry[]>(
      assessmentId ? `/audit-log?assessment_id=${assessmentId}` : "/audit-log",
    ),
};
