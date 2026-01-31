import sqlite3
from typing import Any, Dict, List

from update.extract.dtos import AffairDTO, MemberDTO

class SQLStorage:
    def __init__(self, connection_string: str):
        self._connection_string = connection_string

    def get_member(self, member_id: int):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute
            (
                """
                SELECT * FROM member
                """
            )

    def is_member_inserted(self, *, member_id:int) -> bool:
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM member WHERE member_id = ?"
            params = (member_id,)
            cursor.execute(query, params)
            return len(cursor.fetchall()) > 0;

    def is_affair_inserted(self, *, affair_id:int) -> bool:
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM affair WHERE affair_id = ?"
            params = (affair_id,)
            cursor.execute(query, params)
            return len(cursor.fetchall()) > 0;

    def add_member(self, *, member: MemberDTO):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO member VALUES (?,?,?,?,?,?,?)"
            params = (                
                member.id, 
                member.first_name, 
                member.last_name, 
                member.active, 
                member.party, 
                None,
                member.updated_at
            )

            cursor.execute(query, params)
            conn.commit()


    def add_affair(self, *, member_id: int, affair: AffairDTO):
        with sqlite3.connect(self._connection_string) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO affair VALUES (?,?,?,?,?)"
            params = (affair.id, affair.title, None, member_id, affair.updated_at)
            cursor.execute(query, params)
            conn.commit()

    def add_members(self, members: List[MemberDTO]):
        for member in members:
            if not self.is_member_inserted(member_id=member.id):
                self.add_member(member=member)
                for affair in member.affairs:
                    if not self.is_affair_inserted(affair_id=affair.id):
                        self.add_affair(member_id=member.id, affair=affair)
                    

