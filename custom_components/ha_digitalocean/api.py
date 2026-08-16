import aiohttp
from aiohttp import ClientSession, ClientResponseError

from .const import API_BASE

TIMEOUT = aiohttp.ClientTimeout(total=30)


class DigitalOceanAuthError(Exception):
    pass


class DigitalOceanAPI:
    def __init__(self, token: str, session: ClientSession) -> None:
        self._token = token
        self._session = session
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, path: str, json: dict | None = None) -> dict:
        async with self._session.request(
            method, f"{API_BASE}{path}", headers=self._headers, json=json,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status == 401:
                raise DigitalOceanAuthError("Invalid or revoked API token")
            resp.raise_for_status()
            return await resp.json()

    async def get_account(self) -> dict:
        data = await self._request("GET", "/account")
        return data["account"]

    async def get_droplets(self) -> list[dict]:
        data = await self._request("GET", "/droplets?per_page=200")
        return data["droplets"]

    async def get_droplet(self, droplet_id: int) -> dict:
        data = await self._request("GET", f"/droplets/{droplet_id}")
        return data["droplet"]

    async def droplet_action(self, droplet_id: int, action: str) -> dict:
        data = await self._request(
            "POST", f"/droplets/{droplet_id}/actions", json={"type": action}
        )
        return data["action"]
