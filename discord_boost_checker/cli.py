import argparse
import sys
import os
from .checker import DiscordBadgeChecker

def main():
    parser = argparse.ArgumentParser(description="Fetch Discord user boost and badge info.")
    parser.add_argument("--token", "-t", help="Discord user authorization token", default=os.getenv("DISCORD_TOKEN"))
    parser.add_argument("--user", "-u", help="Target Discord user ID")

    args = parser.parse_args()

    token = args.token
    if not token:
        token = input("Enter your Discord Token: ").strip()

    user_id = args.user
    if not user_id:
        user_id = input("Enter target User ID: ").strip()

    try:
        checker = DiscordBadgeChecker(token)
        profile = checker.get_user_badges(user_id)

        print("\n" + "=" * 45)
        print(f"User: {profile.username} ({profile.user_id})")
        print(f"Account Created: {profile.created_date.strftime('%B %d, %Y')}")
        print("=" * 45)
        
        if profile.boost_date:
            print(f"Server Booster Date : {profile.boost_date} ({profile.boost_date_formatted})")
            print(f"Boosting For        : {profile.boost_days} days (~{profile.boost_months} months)")
        else:
            print("Server Booster Date : None")

        if profile.nitro_date:
            print(f"Nitro Subscriber Date: {profile.nitro_date} ({profile.nitro_date_formatted})")
        else:
            print("Nitro Subscriber Date: None")

        print("\nBadges:")
        if profile.badges:
            for b in profile.badges:
                print(f" - {b}")
        else:
            print(" - None")
        print("=" * 45 + "\n")

    except Exception as e:
        print(f"\n[Error] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
