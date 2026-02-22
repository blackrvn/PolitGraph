import asyncio
import logging
import sqlite3
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.sparse import csr_matrix
from tqdm.auto import tqdm

from update.extract.dtos import AffairDTO, EdgeDTO, MemberDTO
from update.common import util

sqlite3.register_adapter(np.float32, float)

logger = logging.getLogger(__name__)


class SQLStorage:
    def __init__(self, *, connection_string: str, concurrency: int = 10):
        self._connection_string = connection_string
        self._concurrency = concurrency

    def get_member(self, member_id: int):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute
            (
                """
                SELECT * FROM member
                """
            )

    async def is_member_inserted(self, *, member_id:int) -> bool:
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM member WHERE member_id = ?"
            params = (member_id,)
            cursor.execute(query, params)
            return len(cursor.fetchall()) > 0;

    async def is_affair_inserted(self, *, affair_id:int) -> bool:
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM affair WHERE affair_id = ?"
            params = (affair_id,)
            cursor.execute(query, params)
            return len(cursor.fetchall()) > 0;

    async def is_member_updated(self, *, member:MemberDTO):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "SELECT updated_at FROM member WHERE member_id = ?"
            params = (member.id,)
            cursor.execute(query, params)
            updated_at = cursor.fetchone()
            return updated_at is not None and updated_at.__eq__(member.updated_at)

    async def is_affair_updated(self, *, affair:AffairDTO):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "SELECT updated_at FROM affair WHERE affair_id = ?"
            params = (affair.id,)
            cursor.execute(query, params)
            updated_at = cursor.fetchone()
            return updated_at is not None and updated_at.__eq__(affair.updated_at)

    async def add_vector(self, *, tfidf_vector: np.array, w2v_vector: np.array) -> int:
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO vector (tfidf_vector, w2v_vector) VALUES (?, ?)"
            params = (sqlite3.Binary(tfidf_vector.tobytes()), 
                      sqlite3.Binary(w2v_vector.tobytes())
                      )
            cursor.execute(query, params)
            v_id = cursor.lastrowid
            conn.commit()
            return v_id

    async def add_member(self, *, member: MemberDTO, vector_id:int):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO member VALUES (?,?,?,?,?,?,?)"
            params = (                
                member.id, 
                member.first_name, 
                member.last_name, 
                member.active, 
                member.party, 
                member.updated_at,
                vector_id,
            )

            cursor.execute(query, params)
            conn.commit()

    async def add_edge(self, edge: EdgeDTO):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO edge (weight, source_member_id, target_member_id) VALUES (?,?,?)"
            params = (
                edge.weight,
                edge.member_source,
                edge.member_target
                )
            cursor.execute(query, params)
            conn.commit()

    async def add_affair(self, *, member_id: int, affair: AffairDTO, vector_id:int):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO affair VALUES (?,?,?,?,?)"
            params = (
               affair.id,
               affair.title,
               affair.updated_at,
               member_id,
               vector_id,
                )
            cursor.execute(query, params)
            conn.commit()


    async def update_member(self, member:MemberDTO):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = """
                UPDATE member 
                SET first_name=?, last_name=?, active=?, party=?, updated_at=?
                WHERE member_id=?
                """
            params = (                
                member.first_name, 
                member.last_name, 
                member.active, 
                member.party,
                member.updated_at,
                member.id, 
            )
            cursor.execute(query, params)
            query = """
                UPDATE vector
                SET tfidf_vector=?, w2v_vector=?
                FROM member m
                WHERE m.vector_id = vector_id
            """
            params = (
                member.tfidf_vector,
                None
                )
            cursor.execute(query, params)
            conn.commit()


    async def update_affair(self, affair:AffairDTO):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = """
                UPDATE affair 
                SET title=?, updated_at=?
                WHERE affair_id=?
                """
            params = (                
                affair.title, 
                affair.updated_at,
                affair.id
            )
            cursor.execute(query, params)
            query = """
                UPDATE vector
                SET tfidf_vector=?, w2v_vector=?
                FROM affair a
                WHERE a.vector_id = vector_id
            """
            params = (
                affair.tfidf_vector,
                None
                )
            cursor.execute(query, params)
            conn.commit()

    async def delete_edges(self):
        with sqlite3.connect(self._connection_string) as conn:
            conn.execute("DELETE FROM edge")
            conn.commit()
            logger.info("Deleted all existing edges")

    async def load_members_with_vectors(self) -> List[MemberDTO]:
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.member_id, m.first_name, m.last_name, m.active, m.party, m.updated_at,
                       v.w2v_vector
                FROM member m
                JOIN vector v ON m.vector_id = v.vector_id
                WHERE v.w2v_vector IS NOT NULL
            """)
            members = []
            for row in cursor.fetchall():
                member = MemberDTO(
                    id=row[0],
                    first_name=row[1],
                    last_name=row[2],
                    active=row[3],
                    party=row[4],
                    updated_at=row[5],
                    tfidf_vector=None,
                    w2v_vector=np.frombuffer(row[6], dtype=np.float32).reshape(1, -1),
                    _raw={},
                )
                members.append(member)
            return members

    
    async def save_members(self, members: List[MemberDTO]):
        sem = asyncio.Semaphore(self._concurrency)
        lock = asyncio.Lock()
        pbar = tqdm(total=len(members), desc="Saving membes", unit="member")
        
        async def worker(member: MemberDTO) -> None:
            await sem.acquire()
            try:
                if not await self.is_member_inserted(member_id=member.id):
                    v_id = await self.add_vector(tfidf_vector=member.tfidf_vector, w2v_vector=member.w2v_vector)
                    await self.add_member(member=member, vector_id=v_id)
                elif not await self.is_member_updated(member=member):
                    await self.update_member(member=member)
            except (sqlite3.IntegrityError):
                print(f"[{member.id}] could not save member")
            finally:
                sem.release()
                async with lock:
                    pbar.update(1)

        try:
            await asyncio.gather(*(worker(member) for member in members))
        finally:
            pbar.close()



    async def save_affairs(self, docs: List[Tuple[MemberDTO, AffairDTO]]):
        sem = asyncio.Semaphore(self._concurrency)
        lock = asyncio.Lock()
        pbar = tqdm(total=len(docs), desc="Saving affairs", unit="affair")

        async def worker(member: MemberDTO, affair:AffairDTO) -> None:
            await sem.acquire()
            try:
                if not await self.is_affair_inserted(affair_id=affair.id):
                    v_id = await self.add_vector(tfidf_vector=affair.tfidf_vector, w2v_vector=affair.w2v_vector)
                    await self.add_affair(member_id=member.id, affair=affair, vector_id=v_id)
                elif not await self.is_affair_updated(affair=affair):
                    await self.update_affair(affair=affair)
            except (sqlite3.IntegrityError):
                print(f"[{affair.id}] could not save affair")
            finally:
                sem.release()
                async with lock:
                    pbar.update(1)

        try:
            await asyncio.gather(*(worker(member, affair) for (member, affair) in docs))
        finally:
            pbar.close()


    async def save_edges(self, edges: List[EdgeDTO]):

        sem = asyncio.Semaphore(self._concurrency)
        lock = asyncio.Lock()
        pbar = tqdm(total=len(edges), desc="Saving edges", unit="edge")

        async def worker(edge: EdgeDTO) -> None:
            await sem.acquire()
            try:
                await self.add_edge(edge=edge)
            except (sqlite3.IntegrityError):
                print(f"[{edge.id}] could not save edge")
            finally:
                sem.release()
                async with lock:
                    pbar.update(1)

        try:
            await asyncio.gather(*(worker(edge) for edge in edges))
        finally:
            pbar.close()


                    

