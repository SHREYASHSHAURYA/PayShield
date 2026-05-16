from urllib.parse import parse_qs, urlparse


def parse_qr_payload(payload: str) -> dict[str, str]:
    payload = payload.strip()

    if not payload:
        return {}

    if payload.startswith("upi://"):
        parsed = urlparse(payload)
        query = parse_qs(parsed.query)

        result = {}

        if "pa" in query and query["pa"]:
            result["upi_id"] = query["pa"][0]

        if "pn" in query and query["pn"]:
            result["merchant_name"] = query["pn"][0]

        if "am" in query and query["am"]:
            result["amount"] = query["am"][0]

        if "tn" in query and query["tn"]:
            result["note"] = query["tn"][0]

        return result

    return {}
