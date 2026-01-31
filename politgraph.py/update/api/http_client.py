from typing import Any, Dict, Optional, Tuple

import httpx


class HttpClient:
    """
    Reiner Transport:
    - GET
    - JSON decode
    - keine Retry-Logik
    """

    def __init__(self, base_url: str, timeout_seconds: float = 10.0) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/") + "/",
            headers={"Accept": "application/json"},
            timeout=httpx.Timeout(timeout_seconds),
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_json(
        self,
        path_or_url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[int, Optional[Dict[str, Any]]]:
        r = await self._client.get(path_or_url, params=params)

        if not r.is_success:
            return r.status_code, None

        try:
            return r.status_code, r.json()
        except ValueError:
            return r.status_code, None
