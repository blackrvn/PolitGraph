import asyncio
import sqlite3
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.sparse import csr_matrix
from tqdm.auto import tqdm

from update.extract.dtos import AffairDTO, EdgeDTO, MemberDTO
from update.common import util

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
            finally:
                sem.release()
                async with lock:
                    pbar.update(1)

        try:
            await asyncio.gather(*(worker(edge) for edge in edges))
        finally:
            pbar.close()


                    

