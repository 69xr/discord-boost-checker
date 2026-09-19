from dataclasses import dataclass
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any

@dataclass
class UserBadgeProfile:
    user_id: str
    username: Optional[str]
    boost_since: Optional[datetime]
    boost_since_iso: Optional[str]
    nitro_since: Optional[datetime]
    nitro_since_iso: Optional[str]
    badges: List[str]
    raw_data: Dict[str, Any]

    @property
    def boost_date(self) -> Optional[date]:
        """Returns only the boost date (YYYY-MM-DD), removing time and milliseconds."""
        return self.boost_since.date() if self.boost_since else None

    @property
    def boost_date_formatted(self) -> Optional[str]:
        """Returns human-friendly date string like 'September 19, 2024'."""
        return self.boost_since.strftime("%B %d, %Y") if self.boost_since else None

    @property
    def nitro_date(self) -> Optional[date]:
        """Returns only the Nitro start date (YYYY-MM-DD)."""
        return self.nitro_since.date() if self.nitro_since else None

    @property
    def nitro_date_formatted(self) -> Optional[str]:
        """Returns human-friendly date string like 'September 19, 2024'."""
        return self.nitro_since.strftime("%B %d, %Y") if self.nitro_since else None

    @property
    def boost_days(self) -> Optional[int]:
        """Total number of days the user has been boosting."""
        if not self.boost_since:
            return None
        now = datetime.now(timezone.utc)
        return max(0, (now - self.boost_since).days)

    @property
    def boost_months(self) -> Optional[int]:
        """Approximate number of months the user has been boosting."""
        days = self.boost_days
        return days // 30 if days is not None else None

    @property
    def created_at(self) -> datetime:
        """Exact account creation date calculated from Discord Snowflake ID."""
        snowflake = int(self.user_id)
        timestamp_ms = (snowflake >> 22) + 1420070400000
        return datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)

    @property
    def created_date(self) -> date:
        """Account creation date (YYYY-MM-DD)."""
        return self.created_at.date()

    def __repr__(self) -> str:
        return (
            f"<UserBadgeProfile username='{self.username}' "
            f"boost_date='{self.boost_date}' "
            f"badges_count={len(self.badges)}>"
        )
