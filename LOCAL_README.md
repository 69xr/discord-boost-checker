# LOCAL DEVELOPER REFERENCE & ARCHITECTURE MANUAL

This document is an exhaustive reference manual for `discord-boost-checker`. It contains internal technical details, Discord API mechanics, mathematical formulas, code maps, maintenance workflows, and future expansion guides.

---

## 1. Discord API Mechanics & Reverse Engineering

### 1.1 The Profile Endpoint
Unlike official bot endpoints which require privileged intents and mutual server membership, the Discord user client queries the following private REST endpoint whenever a user profile popout is opened:

```http
GET https://discord.com/api/v9/users/{user_id}/profile
```

#### Required Request Headers
Discord strictly filters incoming requests through Cloudflare edge heuristics. To avoid immediate 401/403 rejections:
* `Authorization`: Raw user token string without `Bot` or `Bearer` prefix.
* `Content-Type`: `application/json`
* `User-Agent`: A standard desktop browser User-Agent header. Without this, Discord's anti-scraping system flags bare Python `requests` or `aiohttp` headers.

### 1.2 Raw Payload Structure
The endpoint returns a JSON object containing user metadata. The critical keys utilized by this library are:

```json
{
  "user": {
    "id": "473247429375033364",
    "username": "mOon",
    "discriminator": "0",
    "avatar": "a_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  },
  "premium_since": "2023-05-10T12:00:00.000000+00:00",
  "premium_guild_since": "2024-09-19T20:01:08.798000+00:00",
  "badges": [
    {
      "id": "guild_booster_lvl1",
      "description": "Server boosting since 9/19/24",
      "icon": "8a2636884489a24183706856094b8e88"
    }
  ]
}
```

* `premium_guild_since`: An ISO-8601 timestamp string representing the exact moment the user started server boosting. This is the exact value Discord desktop/mobile clients inspect when rendering the Server Booster hover tooltip.
* `premium_since`: An ISO-8601 timestamp string representing the start of the Discord Nitro subscription.
* `badges`: An array of badge objects containing internal ID, tooltip description, and CDN icon hash.

### 1.3 Discord Snowflake Algorithm (Account Creation Math)
Every Discord ID is a 64-bit integer called a "Snowflake". The timestamp of account creation is encoded directly within the snowflake itself, allowing zero-latency date calculation without extra API queries:

$$\text{timestamp\_ms} = (\text{user\_id} \gg 22) + 1420070400000$$

* `>> 22`: Bitwise right shift by 22 bits removes the internal worker ID, process ID, and increment counter.
* `1420070400000`: Discord Epoch timestamp (January 1, 2015, 00:00:00 UTC in milliseconds).
* Dividing by 1000 yields the Unix timestamp in seconds, which is then parsed into a standard UTC `datetime`.

---

## 2. Codebase Architecture

```text
discord-boost-checker/
│
├── pyproject.toml                     # Modern build configuration (PEP 621)
├── LICENSE                            # MIT License
├── README.md                          # Public GitHub documentation
├── LOCAL_README.md                    # Comprehensive internal technical guide
├── .gitignore                         # Build and cache exclusion rules
│
├── discord_boost_checker/
│   ├── __init__.py                    # Public API exports and version definition
│   ├── models.py                      # UserBadgeProfile dataclass and property logic
│   ├── checker.py                     # Synchronous HTTP client (requests)
│   ├── async_checker.py               # Asynchronous HTTP client (aiohttp)
│   └── cli.py                         # Standalone terminal entry point
│
├── examples/
│   ├── example.py                     # Synchronous script example
│   └── async_example.py               # Asynchronous script example
│
└── dist/                              # Compiled distributions (.whl and .tar.gz)
```

### 2.1 Component Breakdown

#### `discord_boost_checker/models.py`
Defines `UserBadgeProfile` using Python's `@dataclass`. Implements calculated properties:
* `boost_date`: Extracts `.date()` from the boost timestamp, returning `YYYY-MM-DD`.
* `boost_date_formatted`: Formats date as `Month Day, Year` (e.g. `September 19, 2024`).
* `boost_days`: Calculates active streak in days using `(datetime.now(timezone.utc) - boost_since).days`.
* `boost_months`: Calculates approximate months using `boost_days // 30`.
* `created_at` / `created_date`: Implements the Discord Snowflake bitwise math.
* `raw_data`: Retains the complete, unparsed JSON payload from Discord for fallback access.

#### `discord_boost_checker/checker.py`
Synchronous client using `requests.Session`:
* Handles HTTP error codes:
  * `401`: `PermissionError` (Invalid or revoked token).
  * `404`: `ValueError` (User ID does not exist).
  * `429`: `RuntimeError` (Extracts `retry_after` seconds from Discord response).
  * Other: General `RuntimeError` with response text.

#### `discord_boost_checker/async_checker.py`
Asynchronous client designed for non-blocking execution inside event loops:
* Built on `aiohttp.ClientSession`.
* Implements `__aenter__` and `__aexit__` for clean resource cleanup with `async with`.
* Accepts an optional existing `session` parameter, allowing Discord bots to pass their bot's existing `aiohttp.ClientSession` directly.

#### `discord_boost_checker/cli.py`
Command-line interface callable via `discord-boost`:
* Uses Python's built-in `argparse`.
* Checks CLI arguments first (`--token`, `--user`), falls back to environment variable `DISCORD_TOKEN`, and prompts interactively if neither is found.

---

## 3. Integration Patterns

### 3.1 Local Development (Using in Other Projects Without PyPI)
To use this library locally across other projects on your machine without waiting for PyPI:

```powershell
pip install -e C:\Users\moham\Downloads\discord-boost-checker
```
* The `-e` (editable) flag symlinks the package directory. Any edits you make to `discord_boost_checker/` take effect immediately in any script importing it.

### 3.2 Asynchronous Discord Bot Integration (`discord.py`)

```python
import discord
from discord.ext import commands
from discord_boost_checker import AsyncDiscordBadgeChecker

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

USER_TOKEN = "YOUR_DISCORD_USER_TOKEN"

@bot.command(name="checkstreak")
async def check_streak(ctx, target_id: str):
    async with AsyncDiscordBadgeChecker(token=USER_TOKEN) as checker:
        try:
            profile = await checker.get_user_badges(target_id)
            if profile.boost_date:
                await ctx.send(
                    f"User: {profile.username}\n"
                    f"Boost Date: {profile.boost_date_formatted}\n"
                    f"Active Streak: {profile.boost_days} days"
                )
            else:
                await ctx.send(f"User {profile.username} does not have an active booster badge.")
        except Exception as err:
            await ctx.send(f"Error: {err}")

bot.run("YOUR_BOT_TOKEN")
```

---

## 4. Release & Maintenance Lifecycle (Cheat Sheet)

Follow this exact procedure whenever releasing an update to PyPI and GitHub:

### Step 1: Update Version Number
Update the version string in two locations:
1. `pyproject.toml` -> `version = "0.x.x"`
2. `discord_boost_checker/__init__.py` -> `__version__ = "0.x.x"`

### Step 2: Clean and Rebuild Distribution Files
Always remove previous `.whl` and `.tar.gz` artifacts before building:

```powershell
cd C:\Users\moham\Downloads\discord-boost-checker
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
python -m build
```

Verify build validity:
```powershell
python -m twine check dist/*
```

### Step 3: Commit and Push to GitHub

```powershell
git add .
git commit -m "Release v0.x.x"
git push origin main
```

### Step 4: Publish to PyPI

```powershell
python -m twine upload dist/*
```
* **Username**: `__token__`
* **Password**: PyPI API token (`pypi-...`)

---

## 5. Future Expansion Roadmap (v0.4.0+)

The following features can be directly implemented using the existing profile response:

### 5.1 Badge Icon CDN URLs
Discord serves badge assets via:
`https://cdn.discordapp.com/badge-icons/{icon_hash}.png`

Implementation pattern:
```python
@property
def badge_icons(self) -> list[str]:
    return [
        f"https://cdn.discordapp.com/badge-icons/{b['icon']}.png"
        for b in self.raw_data.get("badges", [])
        if "icon" in b
    ]
```

### 5.2 Avatar and Banner CDN URLs
* Avatar: `https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png` (or `.gif` if hash starts with `a_`)
* Banner: `https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.png`

### 5.3 Mutual Guilds Detection
If the target user shares servers with the querying account, Discord populates `mutual_guilds` in the payload:
```json
"mutual_guilds": [
  {"id": "123456789", "nick": "nickname"}
]
```
This can be exposed as `profile.mutual_guild_ids`.
