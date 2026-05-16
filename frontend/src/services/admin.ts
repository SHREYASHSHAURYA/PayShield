import type { AuditLogResponse } from "../types/admin";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

const API_KEY = "dev-pay-shield-key";

export async function fetchAuditLogs(): Promise<AuditLogResponse> {
  const response = await fetch(`${API_BASE_URL}/admin/audit-logs?limit=10`, {
    method: "GET",
    headers: {
      "x-api-key": API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch audit logs");
  }

  return response.json();
}
