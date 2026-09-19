# discord-boost-checker

A Python library to retrieve Discord user profile badges and exact server boost dates. Supports both synchronous execution and asynchronous operation for Discord bot integration.

---

## Installation

```bash
pip install discord-boost-checker
```

---

## Requirements

- Python 3.8+
- requests >= 2.28.0
- aiohttp >= 3.8.0

---

## Quick Start

### 1. Synchronous Usage

Use `DiscordBadgeChecker` for standard standalone scripts.

```python
from discord_boost_checker import DiscordBadgeChecker

TOKEN = "YOUR_DISCORD_USER_TOKEN"
TARGET_USER_ID = "473247429375033364"

checker = DiscordBadgeChecker(token=TOKEN)
profile = checker.get_user_badges(TARGET_USER_ID)

print(f"Username: {profile.username}")
print(f"Account Created: {profile.created_date}")
print(f"Server Booster Date: {profile.boost_date} ({profile.boost_date_formatted})")
print(f"Boosting Streak: {profile.boost_days} days (~{profile.boost_months} months)")
print(f"Nitro Subscriber Date: {profile.nitro_date}")
print(f"Badges: {profile.badges}")
```

---

### 2. Asynchronous Usage (For Discord Bots)

Use `AsyncDiscordBadgeChecker` to avoid blocking the event loop in `discord.py`, `disnake`, or `nextcord`.

```python
import asyncio
from discord_boost_checker import AsyncDiscordBadgeChecker

TOKEN = "YOUR_DISCORD_USER_TOKEN"
TARGET_USER_ID = "473247429375033364"

async def main():
    async with AsyncDiscordBadgeChecker(token=TOKEN) as checker:
        profile = await checker.get_user_badges(TARGET_USER_ID)
        
        print(f"Username: {profile.username}")
        print(f"Server Booster Date: {profile.boost_date}")
        print(f"Streak (Days): {profile.boost_days}")
        print(f"Badges: {profile.badges}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 3. Integration in a discord.py Bot

Example command inside a Discord bot:

```python
import discord
from discord.ext import commands
from discord_boost_checker import AsyncDiscordBadgeChecker

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
USER_TOKEN = "YOUR_DISCORD_USER_TOKEN"

@bot.command(name="boostinfo")
async def boost_info(ctx, user_id: str):
    async with AsyncDiscordBadgeChecker(token=USER_TOKEN) as checker:
        try:
            profile = await checker.get_user_badges(user_id)
            
            if profile.boost_date:
                await ctx.send(
                    f"User: {profile.username}\n"
                    f"Booster Since: {profile.boost_date_formatted}\n"
                    f"Streak: {profile.boost_days} days (~{profile.boost_months} months)"
                )
            else:
                await ctx.send(f"User {profile.username} does not have an active booster badge.")
        except ValueError:
            await ctx.send("User ID not found.")
        except PermissionError:
            await ctx.send("Configured user token is invalid or expired.")
        except RuntimeError as e:
            await ctx.send(f"API Error: {e}")

bot.run("YOUR_BOT_TOKEN")
```

---

### 4. CLI Usage

The package provides a command-line interface directly executable from the terminal.

Interactive prompt:
```bash
discord-boost
```

Passing parameters directly:
```bash
discord-boost --token YOUR_TOKEN --user TARGET_USER_ID
```

---

## API Reference: UserBadgeProfile

When `get_user_badges()` is called, it returns a `UserBadgeProfile` dataclass with the following attributes:

| Property | Type | Description |
| :--- | :--- | :--- |
| `user_id` | `str` | Target Discord snowflake user ID. |
| `username` | `str` | Discord username. |
| `boost_date` | `date \| None` | Server booster date (`YYYY-MM-DD`). |
| `boost_date_formatted` | `str \| None` | Human-readable booster date (e.g. `September 19, 2024`). |
| `boost_since` | `datetime \| None` | Full UTC datetime object including time. |
| `boost_since_iso` | `str \| None` | Raw ISO-8601 string from Discord API. |
| `boost_days` | `int \| None` | Total number of days active server boosting. |
| `boost_months` | `int \| None` | Approximate months active server boosting. |
| `nitro_date` | `date \| None` | Nitro subscription date (`YYYY-MM-DD`). |
| `nitro_date_formatted`| `str \| None` | Human-readable Nitro date. |
| `created_at` | `datetime` | Account creation timestamp calculated from snowflake ID. |
| `created_date` | `date` | Account creation date (`YYYY-MM-DD`). |
| `badges` | `list[str]` | List of badge descriptions/titles. |
| `raw_data` | `dict` | Complete unparsed JSON payload from Discord API. |

---

## Error Handling

The library raises explicit exceptions for API responses:

| Exception | Cause |
| :--- | :--- |
| `PermissionError` | HTTP 401: Invalid or expired authorization token. |
| `ValueError` | HTTP 404: User ID does not exist. |
| `RuntimeError` | HTTP 429: Rate limited, or other unexpected HTTP error codes. |

---

## License

MIT License.
