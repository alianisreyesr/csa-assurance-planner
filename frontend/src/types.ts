export type RiskLevel = "low" | "medium" | "high";
export type CsaClass =
  | "record"
  | "signature"
  | "critical_thinking"
  | "unscripted"
  | "scripted";
export type ReviewDecision = "approve" | "needs_revision";

export interface Summary {
  total_assessments: number;
  high_risk_count: number;
  assurance_items: number;
  approved_reviews: number;
  data_boundary: string;
}

export interface Assessment {
  id: number;
  assessment_ref: string;
  title: string;
  system_name: string;
  gamp_category: string;
  intended_use: string;
  risk_level: RiskLevel | string;
  status: string;
  created_by: string;
  created_at: string;
}

export interface AssuranceItem {
  id: number;
  assessment_id: number;
  requirement_ref: string;
  function_name: string;
  csa_class: CsaClass | string;
  rationale: string;
  test_strategy: string;
  created_at: string;
}

export interface Review {
  id: number;
  assessment_id: number;
  reviewer: string;
  decision: ReviewDecision | string;
  comment: string | null;
  reviewed_at: string;
}

export interface AuditEntry {
  id: number;
  assessment_id: number | null;
  actor: string;
  action: string;
  detail: string | null;
  created_at: string;
}
