// Same-origin by default so HttpOnly session cookies work via Next.js rewrites.
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export async function api<T>(
  path: string,
  options: RequestInit & { json?: unknown } = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.json !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
    body: options.json !== undefined ? JSON.stringify(options.json) : options.body,
  });

  if (!res.ok) {
    let code = "request_failed";
    let message = res.statusText;
    try {
      const data = await res.json();
      code = data?.error?.code || code;
      message = data?.error?.message || message;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, code, message);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export type Me = {
  user: {
    id: string;
    email: string;
    plan: string;
    status: string;
    onboarding_completed_at: string | null;
  };
  profile: {
    display_name: string | null;
    timezone: string;
    role_target: string | null;
  } | null;
  entitlements: Record<string, number | string>;
};

export type Recommendation = {
  action_type: string;
  title: string;
  reason: string;
  estimated_minutes: number;
  practice_item_id: string | null;
  skill_gap: string | null;
  href: string;
};

export type PracticeItem = {
  id: string;
  type: string;
  prompt: string;
  difficulty: string;
  expected_minutes: number;
  competency_id: string | null;
  rubric_version: string;
};

export type Evaluation = {
  id: string;
  attempt_id: string;
  rubric_version: string;
  result_json: {
    overall_score?: number;
    overall_max?: number;
    status_suggestion?: string;
    dimensions?: Record<string, { score: number; max: number; feedback: string }>;
    strengths?: string[];
    gaps?: string[];
    errors?: { error_code: string; description: string; severity: string }[];
    uncertainty?: number;
    evidence_quotes?: string[];
    disclaimer?: string;
  };
  model_version: string;
  confidence: number | null;
  is_provisional: boolean;
};
