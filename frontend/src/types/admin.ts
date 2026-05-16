export interface AuditLogEntry {
  timestamp: string;
  client_id: string;
  session_id: string;
  risk_level: string;
  risk_score: number;
  current_stage: string;
  signal_count: number;
}

export interface AuditLogResponse {
  entries: AuditLogEntry[];
}
