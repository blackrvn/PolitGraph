from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(slots=True)
class AffairDTO:
    id: int
    title: Optional[str]
    updated_at: Optional[str]
    text_raw: Optional[str]
    _raw: Dict[str, Any]

    @staticmethod
    def from_api(data: Dict[str, Any]) -> "AffairDTO":
        return AffairDTO(
            id=int(data["id"]),
            title=data.get("title_de"),
            updated_at=data.get("updated_at"),
            text_raw=data.get("text_raw"),
            _raw=data,
        )

@dataclass(slots=True)
class MemberDTO:
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    active: Optional[bool]
    party: Optional[str]
    updated_at: Optional[str]
    affairs: Optional[AffairDTO]
    _raw: Dict[str, Any]

    @staticmethod
    def from_api(data: Dict[str, Any]) -> "MemberDTO":
        return MemberDTO(
            id=int(data["id"]),
            first_name=data.get("firstname"),
            last_name=data.get("lastname"),
            active=data.get("active"),
            party=data.get("party_de"),
            updated_at=data.get("updated_at"),
            affairs=None,
            _raw=data,
        )

