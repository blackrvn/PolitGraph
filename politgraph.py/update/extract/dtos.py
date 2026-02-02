from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
from gensim.models.doc2vec import TaggedDocument

@dataclass
class AffairDTO:
    id: int
    title: str
    updated_at: str
    text_raw: Optional[str]
    text_clean: Optional[str]
    lemmas: Optional[List[str]]
    tagged_doc: Optional[TaggedDocument]
    tfidf_vector: Optional[List]
    w2v_vector: Optional[List]
    _raw: Dict[str, Any]

    @staticmethod
    def from_api(data: Dict[str, Any]) -> "AffairDTO":
        return AffairDTO(
            id=int(data["id"]),
            title=data.get("title_de"),
            updated_at=data.get("updated_at"),
            text_raw=data.get("text_raw"),
            text_clean=None,
            lemmas=None,
            tagged_doc=None,
            tfidf_vector=None,
            w2v_vector=None,
            _raw=data,
        )

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, value):
        return self.id == value.id


@dataclass
class MemberDTO:
    id: int
    first_name: str
    last_name: str
    active: bool
    party: Optional[str]
    updated_at: str
    tfidf_vector: Optional[List]
    w2v_vector: Optional[List]
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
            tfidf_vector=None,
            w2v_vector=None,
            _raw=data,
        )

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, value):
        return self.id == value.id


@dataclass
class EdgeDTO:
    member_source: int
    member_target: int
    weight: int

