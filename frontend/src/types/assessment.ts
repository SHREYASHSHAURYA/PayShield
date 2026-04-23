export type InteractionType =
  | "text_message"
  | "phone_call"
  | "qr_scan"
  | "upi_id_entry"
  | "collect_request"
  | "payment_link"
  | "app_prompt"
  | "user_confirmation";

export type PaymentMethodType =
  | "none"
  | "qr_code"
  | "upi_id"
  | "collect_request"
  | "payment_link";

export type PaymentDirection = "none" | "send" | "receive";

export type RiskLevel = "low" | "medium" | "high" | "critical";

export type ScamStage = "trust" | "urgency" | "payment" | "extraction";

export type RecommendedAction =
  | "safe_to_continue"
  | "warn_only"
  | "require_extra_confirmation"
  | "recommend_abort";

export interface InteractionEvent {
  event_id: string;
  timestamp: string;
  interaction_type: InteractionType;
  content_text: string | null;
  source_label: string | null;
  metadata: Record<string, string>;
}

export interface PaymentContext {
  payment_method: PaymentMethodType;
  payment_direction: PaymentDirection;
  amount: number | null;
  currency: string;
  upi_id: string | null;
  collect_request_present: boolean;
  qr_present: boolean;
  payment_link_present: boolean;
  merchant_name: string | null;
  note: string | null;
}

export interface UserFlags {
  user_expects_money: boolean;
  user_initiated_contact: boolean;
  trusted_beneficiary: boolean;
  first_time_beneficiary: boolean;
  user_confirms_pressure: boolean;
  user_confirms_identity_verified: boolean;
}

export interface AssessmentRequest {
  session_id: string;
  device_timestamp: string;
  locale: string;
  interaction_events: InteractionEvent[];
  payment_context: PaymentContext;
  user_flags: UserFlags;
}

export interface TriggeredSignal {
  signal_type: string;
  confidence: number;
  source_event_id: string | null;
  evidence: string;
}

export interface StageState {
  current_stage: ScamStage;
  completed_stages: ScamStage[];
}

export interface AssessmentResponse {
  request_id: string;
  session_id: string;
  risk_level: RiskLevel;
  risk_score: number;
  current_stage: ScamStage;
  recommended_action: RecommendedAction;
  should_warn_user: boolean;
  triggered_signals: TriggeredSignal[];
  stage_state: StageState;
  explanation: string[];
}
