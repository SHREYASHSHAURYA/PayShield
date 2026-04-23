import type {
  AssessmentRequest,
  AssessmentResponse,
} from "../types/assessment";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export async function assessRisk(
  payload: AssessmentRequest,
): Promise<AssessmentResponse> {
  const response = await fetch(`${API_BASE_URL}/risk/assess`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Risk assessment request failed");
  }

  return response.json();
}
