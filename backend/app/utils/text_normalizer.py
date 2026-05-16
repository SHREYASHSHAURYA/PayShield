import re

ROMANIZED_REPLACEMENTS = {
    "jaldi": "urgent",
    "turant": "immediately",
    "abhi": "right now",
    "otp batao": "share otp",
    "otp bataye": "share otp",
    "otp share karo": "share otp",
    "paise bhejo": "send money",
    "paise transfer karo": "transfer money",
    "qr scan karo": "scan qr",
    "account block ho jayega": "account will be blocked",
    "account band ho jayega": "account will be blocked",
    "kyc update karo": "update kyc",
    "refund ke liye": "for refund",
    "request approve karo": "approve request",
    "collect request approve karo": "approve collect request",
    "payment karo": "make payment",
    "verify karo": "verify now",
    "customer care se bol raha hu": "bank customer care",
    "bank se bol raha hu": "bank customer care",
}


def normalize_text(text: str) -> str:
    normalized = text.strip().lower()
    normalized = re.sub(r"[\r\n\t]+", " ", normalized)
    normalized = re.sub(r"[^\w\s@:/.-]", " ", normalized)

    for source, target in ROMANIZED_REPLACEMENTS.items():
        normalized = normalized.replace(source, target)

    normalized = re.sub(r"\s+", " ", normalized)
    return normalized
