import requests
from datetime import datetime
from typing import Optional, Union
from .models import UserBadgeProfile

class DiscordBadgeChecker:
    """
    Client for querying Discord user badges and exact boost timestamps.
    """
    BASE_URL = "https://discord.com/api/v9"

    def __init__(self, token: str, user_agent: Optional[str] = None):
        """
        :param token: Discord user token.
        :param user_agent: Optional custom User-Agent string.
        """
        if not token or not token.strip():
            raise ValueError("Token must not be empty.")

        self.token = token.strip()
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": user_agent or (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

    def get_user_badges(self, user_id: Union[str, int]) -> UserBadgeProfile:
        """
        Fetches the profile and badge data for a given Discord user ID.

        :param user_id: The Discord snowflake ID of the target user.
        :return: UserBadgeProfile instance.
        """
        uid = str(user_id).strip()
        url = f"{self.BASE_URL}/users/{uid}/profile"

        response = requests.get(url, headers=self.headers)

        if response.status_code == 401:
            raise PermissionError("Unauthorized: The provided Discord token is invalid or expired.")
        elif response.status_code == 404:
            raise ValueError(f"User with ID {uid} not found.")
        elif response.status_code == 429:
            data = response.json()
            retry_after = data.get("retry_after", 5)
            raise RuntimeError(f"Rate limited by Discord. Please retry after {retry_after} seconds.")
        elif response.status_code != 200:
            raise RuntimeError(f"Discord API error [{response.status_code}]: {response.text}")

        data = response.json()
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
