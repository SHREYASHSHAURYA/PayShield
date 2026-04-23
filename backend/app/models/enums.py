from enum import Enum


class SignalType(str, Enum):
    URGENCY = "urgency"
    IMPERSONATION = "impersonation"
    AUTHORITY_CLAIM = "authority_claim"
    REWARD_BAIT = "reward_bait"
    FEAR_PRESSURE = "fear_pressure"
    SECRECY_REQUEST = "secrecy_request"
    QR_PAYMENT_PROMPT = "qr_payment_prompt"
    UPI_ID_SHARED = "upi_id_shared"
    COLLECT_REQUEST_DETECTED = "collect_request_detected"
    PAYMENT_LINK_SHARED = "payment_link_shared"
    REMOTE_APP_REQUEST = "remote_app_request"
    REFUND_CLAIM = "refund_claim"
    JOB_OFFER = "job_offer"
    KYC_CLAIM = "kyc_claim"
    ACCOUNT_BLOCK_CLAIM = "account_block_claim"
    PAYMENT_REQUEST = "payment_request"
    TRANSACTION_CONFIRMATION_REQUEST = "transaction_confirmation_request"


class ScamStage(str, Enum):
    TRUST = "trust"
    URGENCY = "urgency"
    PAYMENT = "payment"
    EXTRACTION = "extraction"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InteractionType(str, Enum):
    TEXT_MESSAGE = "text_message"
    PHONE_CALL = "phone_call"
    QR_SCAN = "qr_scan"
    UPI_ID_ENTRY = "upi_id_entry"
    COLLECT_REQUEST = "collect_request"
    PAYMENT_LINK = "payment_link"
    APP_PROMPT = "app_prompt"
    USER_CONFIRMATION = "user_confirmation"


class PaymentMethodType(str, Enum):
    NONE = "none"
    QR_CODE = "qr_code"
    UPI_ID = "upi_id"
    COLLECT_REQUEST = "collect_request"
    PAYMENT_LINK = "payment_link"


class PaymentDirection(str, Enum):
    NONE = "none"
    SEND = "send"
    RECEIVE = "receive"


class RecommendedAction(str, Enum):
    SAFE_TO_CONTINUE = "safe_to_continue"
    WARN_ONLY = "warn_only"
    REQUIRE_EXTRA_CONFIRMATION = "require_extra_confirmation"
    RECOMMEND_ABORT = "recommend_abort"
