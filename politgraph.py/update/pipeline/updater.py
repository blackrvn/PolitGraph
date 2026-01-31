import asyncio
from typing import Any, Dict, List

from tqdm.auto import tqdm

from update.api.parliament_api import ParliamentApi
from update.extract.dtos import MemberDTO, AffairDTO
from update.extract.text_extractors import extract_eingereichter_text_de


class Updater:
    """
    Returns a list of members.
    The members contain affairs.
    """

    def __init__(self, api: ParliamentApi) -> None:
        self.api = api

    async def fetch_documents(self, *, concurrency: int = 10) -> List[MemberDTO]:
        member_ids = await self.api.list_active_member_ids()
        member_ids = list(member_ids)
        sem = asyncio.Semaphore(concurrency)

        docs: List[MemberDTO] = []
        lock = asyncio.Lock()

        pbar = tqdm(total=len(member_ids), desc="Processing members", unit="member")

        async def worker(member_id: int) -> None:
            await sem.acquire()
            try:
                member_raw = await self.api.get_member(member_id)
                if member_raw is None:
                    return

                member = MemberDTO.from_api(member_raw)

                affair_ids = await self.api.list_affair_ids_for_member(member_id)
                affairs: List[AffairDTO] = []

                for aid in affair_ids:
                    affair_raw = await self.api.get_affair_with_texts(aid)
                    if affair_raw is None:
                        continue

                    text_de = extract_eingereichter_text_de(affair_raw)
                    if text_de is None:
                        continue

                    affair_raw["text_raw"] = text_de
                    affair = AffairDTO.from_api(affair_raw)
                    affairs.append(affair)

                if len(affairs) > 0:
                    member.affairs = affairs
                    async with lock:
                        docs.append(member)

            finally:
                sem.release()
                async with lock:
                    pbar.update(1)

        try:
            await asyncio.gather(*(worker(member_id) for member_id in member_ids))
        finally:
            pbar.close()

        return docs
