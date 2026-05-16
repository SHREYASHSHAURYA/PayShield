from app.utils.text_normalizer import normalize_text


def extract_visible_text(metadata: dict[str, str]) -> str:
    ocr_text = metadata.get("ocr_text", "").strip()
    qr_payload = metadata.get("qr_payload", "").strip()
    screen_text = metadata.get("screen_text", "").strip()

    combined = " ".join(part for part in [ocr_text, qr_payload, screen_text] if part)
    return normalize_text(combined) if combined else ""
