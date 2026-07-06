import asyncio
import logging
from typing import Any, Dict, List, Tuple

from tqdm.auto import tqdm

from update.api.parliament_api import ParliamentApi
from update.extract.dtos import MemberDTO, AffairDTO
from update.extract.text_extractors import extract_text_de
from update.storage.sqlite_storage import SQLStorage

logger = logging.getLogger(__name__)


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

    async def fetch_documents(self, *, concurrency: int = 10, offset: int= 0, active: bool = True) -> Tuple[List[Tuple[MemberDTO, AffairDTO]], List[MemberDTO]]:
        member_ids = await self._api.list_member_ids(active=active, offset=offset)
        member_ids = list(member_ids)
        sem = asyncio.Semaphore(concurrency)

        docs = []
        members = []
        lock = asyncio.Lock()

        stats = {"members": 0, "affairs": 0, "invalid": 0, "skipped": 0}

        pbar = tqdm(total=len(member_ids), desc="Retrieving members", unit="member")

        def _refresh_postfix() -> None:
            pbar.set_postfix(
                affairs=stats["affairs"],
                invalid=stats["invalid"],
                skipped=stats["skipped"],
                refresh=False,
            )

        async def worker(member_id: int) -> None:
            await sem.acquire()
            try:
                member_raw = await self._api.get_member(member_id)
                if member_raw is None:
                    return

                member = MemberDTO.from_api(member_raw)
                member._raw = {}

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
                        affair._raw = {}
                        if(affair.is_valid()):
                            async with lock:
                                docs.append((member, affair))
                                stats["affairs"] += 1
                                affair_count += 1
                        else:
                            async with lock:
                                stats["invalid"] += 1
                            logger.debug(f"[{affair.id}] Affair is not valid")

                    if affair_count > 0:
                        async with lock:
                            members.append(member)
                            stats["members"] += 1

                else:
                    async with lock:
                        stats["skipped"] += 1
                    logger.debug(f"[{member.id}] Is already updated")

            finally:
                sem.release()
                async with lock:
                    pbar.update(1)
                    _refresh_postfix()

        try:
            await asyncio.gather(*(worker(member_id) for member_id in member_ids))
        finally:
            pbar.close()

        logger.info(
            f"Fetched {stats['affairs']} affairs from {stats['members']} members "
            f"({stats['skipped']} members up-to-date, {stats['invalid']} affairs invalid)"
        )

        return (docs, members)
