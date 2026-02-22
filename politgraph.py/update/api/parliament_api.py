from typing import Any, Dict, List, Optional, Set

import httpx

from update.api.http_client import HttpClient


class ParliamentApi:

    def __init__(self, http: HttpClient) -> None:
        self.http = http

    async def _get_paginated_ids(
        self,
        entry_node: str,
        *,
        tolerate_500: bool = False,
    ) -> Set[int]:
        ids: Set[int] = set()

        try:
            status, container = await self.http.get_json(entry_node)
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError):
            return ids

        if container is None:
            if tolerate_500 and status == 500:
                return ids
            return ids

        while True:
            for item in container.get("data", []):
                if "id" in item:
                    ids.add(int(item["id"]))

            meta = container.get("meta") or {}
            next_page = meta.get("next_page") or meta.get("nextPage")
            if not next_page:
                break

            try:
                status, container = await self.http.get_json(next_page)
            except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError):
                break

            if container is None:
                if tolerate_500 and status == 500:
                    break
                break

        return ids

    async def list_active_member_ids(self) -> Set[int]:
        return await self._get_paginated_ids(
            "persons/?body_key=CHE&active=true"
        )

    async def list_member_ids(self, offset: int, active: bool) -> Set[int]:
        return await self._get_paginated_ids(
            f"persons/?body_key=CHE&active={'true' if active else 'false'}&offset={offset}"
        )

    async def get_member(self, member_id: int) -> Optional[Dict[str, Any]]:
        try:
            _, data = await self.http.get_json(
                f"persons/{member_id}",
                params={
                    "lang": "de",
                    "lang_format":"flat"
                }
            )
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError):
            return None
        return data

    async def list_affair_ids_for_member(self, member_id: int) -> Set[int]:
        return await self._get_paginated_ids(
            f"persons/{member_id}/affairs?limit=300",
            tolerate_500=True,
        )

    async def get_affair_with_texts(self, affair_id: int) -> Optional[Dict[str, Any]]:
        try:
            _, data = await self.http.get_json(
                f"affairs/{affair_id}",
                params=
                {
                    "expand": "texts",
                    "lang": "de",
                    "lang_format":"flat"
                },
            )
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError):
            return None
        return data
