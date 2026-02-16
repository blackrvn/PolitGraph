import asyncio
from typing import Any, Dict, List, Tuple

from tqdm.auto import tqdm

from update.api.parliament_api import ParliamentApi
from update.extract.dtos import MemberDTO, AffairDTO
from update.extract.text_extractors import extract_text_de
from update.storage.sqlite_storage import SQLStorage


class Updater:
    """
    Returns a tuple, containing a list of documents and a list of members.
    The following format is applied:
    (
        [
            (member_1, affair_1),
            (member_1, affair_2),
            (member_3, affair_1),
            ...
        ],
        [
            member_1,
            member_2,
            ...
        ]
    )
    """

    def __init__(self, api: ParliamentApi, storage: SQLStorage) -> None:
        self._api = api
        self._storage = storage

    async def fetch_documents(self, *, concurrency: int = 10) -> Tuple[List[Tuple[MemberDTO, AffairDTO]], List[MemberDTO]]:
        member_ids = await self._api.list_active_member_ids()
        member_ids = list(member_ids)
        sem = asyncio.Semaphore(concurrency)

        docs = []
        members = []
        lock = asyncio.Lock()

        pbar = tqdm(total=len(member_ids), desc="Retrieving members", unit="member")

        async def worker(member_id: int) -> None:
            await sem.acquire()
            try:
                member_raw = await self._api.get_member(member_id)
                if member_raw is None:
                    return

                member = MemberDTO.from_api(member_raw)

                if not await self._storage.is_member_updated(member=member):
                    affair_ids = await self._api.list_affair_ids_for_member(member_id)
                    affair_count = 0

                    for aid in affair_ids:
                        affair_raw = await self._api.get_affair_with_texts(aid)
                        if affair_raw is None:
                            continue

                        text_de = extract_text_de(affair_raw)
                        if text_de is None:
                            continue

                        affair_raw["text_raw"] = text_de
                        affair = AffairDTO.from_api(affair_raw)
                        async with lock:
                            docs.append((member, affair))
                            affair_count += 1
                            
                    if affair_count > 0:
                        async with lock:
                            members.append(member)

                else:
                    print(f"[{member.id}] Is already updated")

            finally:
                sem.release()
                async with lock:
                    pbar.update(1)

        try:
            await asyncio.gather(*(worker(member_id) for member_id in member_ids))
        finally:
            pbar.close()

        return (docs, members)
