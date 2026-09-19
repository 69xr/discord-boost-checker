import asyncio
import os
from discord_boost_checker import AsyncDiscordBadgeChecker

async def main():
    TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_TOKEN_HERE")
    TARGET_USER_ID = "473247429375033364"

    # Use as async context manager (auto closes aiohttp session)
    async with AsyncDiscordBadgeChecker(token=TOKEN) as checker:
        profile = await checker.get_user_badges(TARGET_USER_ID)
        
        print(f"Username            : {profile.username}")
        print(f"Account Created     : {profile.created_date}")
        print(f"Server Booster Date : {profile.boost_date} ({profile.boost_date_formatted})")
        print(f"Boosting Streak     : {profile.boost_days} days (~{profile.boost_months} months)")
        print(f"Badges              : {profile.badges}")

if __name__ == "__main__":
    asyncio.run(main())
