# Am 08.03.2026 mit Claude erstellt.
# sqlite_storage wurde als eingabe verwendet, mit der Anweisung diese auf postgresql umzustellen.
import asyncio
import logging
from typing import List, Tuple

import numpy as np
import psycopg
from psycopg.rows import tuple_row
from psycopg_pool import AsyncConnectionPool
from tqdm.auto import tqdm

from update.extract.dtos import AffairDTO, EdgeDTO, MemberDTO
from update.common import util

logger = logging.getLogger(__name__)


class SQLStorage:
    def __init__(self, *, connection_string: str, concurrency: int = 10):
        self._concurrency = concurrency
        self._pool = AsyncConnectionPool(
            connection_string,
            min_size=2,
            max_size=concurrency,
            kwargs={"row_factory": tuple_row},
            open=False,
        )

    async def __aenter__(self):
        await self._pool.open()
        return self

    async def __aexit__(self, *_):
        await self._pool.close()

    async def get_member(self, member_id: int):
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM member")

    async def is_member_inserted(self, *, member_id: int) -> bool:
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM member WHERE member_id = %s", (member_id,)
                )
                return await cur.fetchone() is not None

    async def is_affair_inserted(self, *, affair_id: int) -> bool:
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM affair WHERE affair_id = %s", (affair_id,)
                )
                return await cur.fetchone() is not None

    async def is_member_updated(self, *, member: MemberDTO) -> bool:
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT updated_at FROM member WHERE member_id = %s",
                    (member.id,),
                )
                row = await cur.fetchone()
                return row is not None and row[0] == member.updated_at

    async def is_affair_updated(self, *, affair: AffairDTO) -> bool:
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT updated_at FROM affair WHERE affair_id = %s",
                    (affair.id,),
                )
                row = await cur.fetchone()
                return row is not None and row[0] == affair.updated_at

    async def add_vector(self, *, tfidf_vector: np.ndarray, w2v_vector: np.ndarray) -> int:
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO vector (tfidf_vector, w2v_vector)
                    VALUES (%s, %s)
                    RETURNING vector_id
                    """,
                    (
                        tfidf_vector.tobytes() if tfidf_vector is not None else None,
                        w2v_vector.tobytes() if w2v_vector is not None else None,
                    ),
                )
                row = await cur.fetchone()
                await conn.commit()
                return row[0]

    async def add_member(self, *, member: MemberDTO, vector_id: int):
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO member (member_id, first_name, last_name, active, party, updated_at, vector_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        member.id,
                        member.first_name,
                        member.last_name,
                        member.active,
                        member.party,
                        member.updated_at,
                        vector_id,
                    ),
                )
                await conn.commit()

    async def add_edge(self, edge: EdgeDTO):
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO edge (weight, source_member_id, target_member_id)
                    VALUES (%s, %s, %s)
                    """,
                    (edge.weight, edge.member_source, edge.member_target),
                )
                await conn.commit()

    async def add_affair(self, *, member_id: int, affair: AffairDTO, vector_id: int):
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO affair (affair_id, title, updated_at, member_id, vector_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        affair.id,
                        affair.title,
                        affair.updated_at,
                        member_id,
                        vector_id,
                    ),
                )
                await conn.commit()

    async def update_member(self, member: MemberDTO):
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE member
                    SET first_name = %s, last_name = %s, active = %s, party = %s, updated_at = %s
                    WHERE member_id = %s
                    """,
                    (
                        member.first_name,
                        member.last_name,
                        member.active,
                        member.party,
                        member.updated_at,
                        member.id,
                    ),
                )
                await cur.execute(
                    """
                    UPDATE vector
                    SET tfidf_vector = %s, w2v_vector = %s
                    FROM member m
                    WHERE m.vector_id = vector.vector_id
                      AND m.member_id = %s
                    """,
                    (
                        member.tfidf_vector.tobytes() if member.tfidf_vector is not None else None,
                        member.w2v_vector.tobytes() if member.w2v_vector is not None else None,
                        member.id,
                    ),
                )
                await conn.commit()

    async def update_affair(self, affair: AffairDTO):
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE affair
                    SET title = %s, updated_at = %s
                    WHERE affair_id = %s
                    """,
                    (affair.title, affair.updated_at, affair.id),
                )
                await cur.execute(
                    """
                    UPDATE vector
                    SET tfidf_vector = %s, w2v_vector = %s
                    FROM affair a
                    WHERE a.vector_id = vector.vector_id
                      AND a.affair_id = %s
                    """,
                    (
                        affair.tfidf_vector.tobytes() if affair.tfidf_vector is not None else None,
                        affair.w2v_vector.tobytes() if affair.w2v_vector is not None else None,
                        affair.id,
                    ),
                )
                await conn.commit()

    async def delete_edges(self):
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM edge")
                await conn.commit()
                logger.info("Deleted all existing edges")

    async def load_members_with_vectors(self) -> List[MemberDTO]:
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT m.member_id, m.first_name, m.last_name, m.active, m.party, m.updated_at,
                           v.w2v_vector
                    FROM member m
                    JOIN vector v ON m.vector_id = v.vector_id
                    WHERE v.w2v_vector IS NOT NULL
                    """
                )
                rows = await cur.fetchall()

        members = []
        for row in rows:
            member = MemberDTO(
                id=row[0],
                first_name=row[1],
                last_name=row[2],
                active=row[3],
                party=row[4],
                updated_at=row[5],
                tfidf_vector=None,
                w2v_vector=np.frombuffer(bytes(row[6]), dtype=np.float32).reshape(1, -1),
                _raw={},
            )
            members.append(member)
        return members

    async def save_members(self, members: List[MemberDTO]):
        sem = asyncio.Semaphore(self._concurrency)
        lock = asyncio.Lock()
        pbar = tqdm(total=len(members), desc="Saving members", unit="member")
        stats = {"new": 0, "updated": 0, "failed": 0}

        async def worker(member: MemberDTO) -> None:
            async with sem:
                try:
                    if not await self.is_member_inserted(member_id=member.id):
                        v_id = await self.add_vector(
                            tfidf_vector=member.tfidf_vector,
                            w2v_vector=member.w2v_vector,
                        )
                        await self.add_member(member=member, vector_id=v_id)
                        stats["new"] += 1
                    elif not await self.is_member_updated(member=member):
                        await self.update_member(member=member)
                        stats["updated"] += 1
                except psycopg.errors.UniqueViolation:
                    stats["failed"] += 1
                    logger.debug(f"[{member.id}] could not save member")
                finally:
                    async with lock:
                        pbar.update(1)
                        pbar.set_postfix(new=stats["new"], updated=stats["updated"], failed=stats["failed"], refresh=False)

        try:
            await asyncio.gather(*(worker(member) for member in members))
        finally:
            pbar.close()

        logger.info(f"Saved members: {stats['new']} new, {stats['updated']} updated, {stats['failed']} failed")

    async def save_affairs(self, docs: List[Tuple[MemberDTO, AffairDTO]]):
        sem = asyncio.Semaphore(self._concurrency)
        lock = asyncio.Lock()
        pbar = tqdm(total=len(docs), desc="Saving affairs", unit="affair")
        stats = {"new": 0, "updated": 0, "failed": 0}

        async def worker(member: MemberDTO, affair: AffairDTO) -> None:
            async with sem:
                try:
                    if not await self.is_affair_inserted(affair_id=affair.id):
                        v_id = await self.add_vector(
                            tfidf_vector=affair.tfidf_vector,
                            w2v_vector=affair.w2v_vector,
                        )
                        await self.add_affair(member_id=member.id, affair=affair, vector_id=v_id)
                        stats["new"] += 1
                    elif not await self.is_affair_updated(affair=affair):
                        await self.update_affair(affair=affair)
                        stats["updated"] += 1
                except psycopg.errors.UniqueViolation:
                    stats["failed"] += 1
                    logger.debug(f"[{affair.id}] could not save affair")
                finally:
                    async with lock:
                        pbar.update(1)
                        pbar.set_postfix(new=stats["new"], updated=stats["updated"], failed=stats["failed"], refresh=False)

        try:
            await asyncio.gather(*(worker(member, affair) for (member, affair) in docs))
        finally:
            pbar.close()

        logger.info(f"Saved affairs: {stats['new']} new, {stats['updated']} updated, {stats['failed']} failed")

    async def save_edges(self, edges: List[EdgeDTO]):
        sem = asyncio.Semaphore(self._concurrency)
        lock = asyncio.Lock()
        pbar = tqdm(total=len(edges), desc="Saving edges", unit="edge")
        stats = {"saved": 0, "failed": 0}

        async def worker(edge: EdgeDTO) -> None:
            async with sem:
                try:
                    await self.add_edge(edge=edge)
                    stats["saved"] += 1
                except psycopg.errors.UniqueViolation:
                    stats["failed"] += 1
                    logger.debug(f"[{edge.member_source}->{edge.member_target}] could not save edge")
                finally:
                    async with lock:
                        pbar.update(1)
                        pbar.set_postfix(saved=stats["saved"], failed=stats["failed"], refresh=False)

        try:
            await asyncio.gather(*(worker(edge) for edge in edges))
        finally:
            pbar.close()

        logger.info(f"Saved edges: {stats['saved']} saved, {stats['failed']} failed")
