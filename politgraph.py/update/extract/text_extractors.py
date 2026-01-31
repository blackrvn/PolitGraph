from typing import Any, Dict, Optional


def extract_eingereichter_text_de(affair_response: Dict[str, Any]) -> Optional[str]:
    texts = affair_response.get("texts") or {}
    data = texts.get("data") or []

    for entry in data:
        if entry.get("type_de") == "Eingereichter Text":
            return entry.get("text_de")

    return None
