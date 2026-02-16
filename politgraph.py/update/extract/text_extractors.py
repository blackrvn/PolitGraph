import string
from typing import Any, Dict, Optional


def extract_text_de(affair_response: Dict[str, Any]) -> Optional[str]:
    texts = affair_response.get("texts") or {}
    data = texts.get("data") or []
    t = ""
    for entry in data:
        text_de = entry.get("text_de")
        if(text_de != None):
            t += " " + text_de

    if t != "":
        return t
