from typing import Any, Dict, Optional


class MemberDTO:
    @staticmethod
    def from_api(data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": int(data["id"]),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "active": data.get("active"),
            "party": data.get("party"),
            "updated_at": data.get("updated_at"),
            "_raw": data,
        }


class AffairDTO:
    @staticmethod
    def from_api(data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": int(data["id"]),
            "title": data.get("title_de"),
            "updated_at": data.get("updated_at"),
            "text_raw": None,
            "_raw": data,
        }
