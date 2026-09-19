import aiohttp
from datetime import datetime
from typing import Optional, Union
from .models import UserBadgeProfile

class AsyncDiscordBadgeChecker:
    """
    Asynchronous client for querying Discord user badges and exact boost timestamps.
    Ideal for Discord bots (discord.py, disnake, nextcord, etc.) to prevent event loop blocking.
    """
    BASE_URL = "https://discord.com/api/v9"

    def __init__(
        self,
        token: str,
        session: Optional[aiohttp.ClientSession] = None,
        user_agent: Optional[str] = None
    ):
        """
        :param token: Discord user authorization token.
        :param session: Optional existing aiohttp.ClientSession (e.g. from your bot).
        :param user_agent: Optional custom User-Agent string.
        """
        if not token or not token.strip():
            raise ValueError("Token must not be empty.")

        self.token = token.strip()
        self._session = session
        self._owns_session = session is None
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": user_agent or (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)
            self._owns_session = True
        return self._session

    async def get_user_badges(self, user_id: Union[str, int]) -> UserBadgeProfile:
        """
        Asynchronously fetches profile and badge data for a given Discord user ID.

        :param user_id: The Discord snowflake ID of the target user.
        :return: UserBadgeProfile instance.
        """
        uid = str(user_id).strip()
        url = f"{self.BASE_URL}/users/{uid}/profile"
        session = await self._get_session()

        async with session.get(url, headers=self.headers) as response:
            if response.status == 401:
                raise PermissionError("Unauthorized: The provided Discord token is invalid or expired.")
            elif response.status == 404:
                raise ValueError(f"User with ID {uid} not found.")
            elif response.status == 429:
                data = await response.json()
                retry_after = data.get("retry_after", 5)
                raise RuntimeError(f"Rate limited by Discord. Please retry after {retry_after} seconds.")
            elif response.status != 200:
                text = await response.text()
                raise RuntimeError(f"Discord API error [{response.status}]: {text}")

            data = await response.json()

        raw_boost = data.get("premium_guild_since")
        raw_nitro = data.get("premium_since")

        boost_dt = None
        if raw_boost:
            try:
                boost_dt = datetime.fromisoformat(raw_boost.replace("Z", "+00:00"))
            except ValueError:
                pass

        nitro_dt = None
        if raw_nitro:
            try:
                nitro_dt = datetime.fromisoformat(raw_nitro.replace("Z", "+00:00"))
            except ValueError:
                pass

        badge_list = [
            b.get("description", b.get("id"))
            for b in data.get("badges", [])
            if isinstance(b, dict)
        ]

        username = data.get("user", {}).get("username")

        return UserBadgeProfile(
            user_id=uid,
            username=username,
            boost_since=boost_dt,
            boost_since_iso=raw_boost,
            nitro_since=nitro_dt,
            nitro_since_iso=raw_nitro,
            badges=badge_list,
            raw_data=data
        )

    async def close(self):
        """Closes the underlying aiohttp session if created by this instance."""
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
