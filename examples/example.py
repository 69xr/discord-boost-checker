import os
from discord_boost_checker import DiscordBadgeChecker

# Option 1: Pass token directly
TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_TOKEN_HERE")
TARGET_USER_ID = "473247429375033364"

checker = DiscordBadgeChecker(token=TOKEN)

try:
    profile = checker.get_user_badges(TARGET_USER_ID)
    print(f"Username            : {profile.username}")
    print(f"Account Created     : {profile.created_date}")
    print(f"Server Booster Date : {profile.boost_date}  ({profile.boost_date_formatted})")
    print(f"Boosting Streak     : {profile.boost_days} days (~{profile.boost_months} months)")
    print(f"Nitro Date          : {profile.nitro_date}")
    print(f"Badges              : {profile.badges}")
except Exception as e:
    print("Error:", e)
