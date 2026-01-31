import asyncio
from typing import Any, Dict, List

from update.api.parliament_api import ParliamentApi
from update.extract.dtos import MemberDTO, AffairDTO
from update.extract.text_extractors import extract_eingereichter_text_de


class Updater:
    """
    Returns a list of dictionairies, that represent a member.
    The following structure is used:
    [
      {
        "member": {...},
        "affair": {
          "id": ...,
          "text_raw": "<p>Der Bundesrat wird beauftragt ...</p>",
          ...
        }
      },
      ...
    ]
    """
    def __init__(self, api: ParliamentApi) -> None:
        self.api = api

    async def fetch_documents(self, *, concurrency: int = 10) -> List[Dict[str, Any]]:
        member_ids = await self.api.list_active_member_ids()
        sem = asyncio.Semaphore(concurrency)

        docs: List[Dict[str, Any]] = []

        # Asynchron alle affairs pro member sammeln.
        # members werden nur zur doc liste hinzugefügt, wenn sie über valide afairs verfügen
        async def worker(member_id: int) -> None:
            await sem.acquire()
            try:
                member_raw = await self.api.get_member(member_id)
                if member_raw is None:
                    return

                member = MemberDTO.from_api(member_raw)

                affair_ids = await self.api.list_affair_ids_for_member(member_id)
                for aid in affair_ids:
                    affair_raw = await self.api.get_affair_with_texts(aid)
                    if affair_raw is None:
                        continue

                    text_de = extract_eingereichter_text_de(affair_raw)
                    if text_de is None:
                        continue

                    affair_raw["text_raw"] = text_de
                    affair = AffairDTO.from_api(affair_raw)

                    docs.append(
                        {
                            "member": member,
                            "affair": affair,
                        }
                    )
            finally:
                sem.release()

        await asyncio.gather(*(worker(member_id) for member_id in member_ids))
        return docs

