import discord
from discord.ext import commands
import csv
import os
import argparse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import sys
import asyncio

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ Error: Set BOT_TOKEN in .env file!")
    sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch Discord channel messages within a date range.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python fetch_messages.py -c 123456789012345678 -s "2024-01-01T00:00:00Z" -e "2024-06-30T23:59:59Z"
  python fetch_messages.py -c 123456789012345678 --help
        """
    )
    parser.add_argument("-c", "--channel-id", type=int, required=True, help="Target channel ID")
    parser.add_argument("-s", "--start-date", type=str, default=None, help="Start datetime (ISO 8601 format. Default: 7 days ago)")
    parser.add_argument("-e", "--end-date", type=str, default=None, help="End datetime (ISO 8601 format. Default: today)")
    args = parser.parse_args()

    def parse_date(iso_str):
        if not iso_str:
            return None
        try:
            return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        except ValueError:
            print(f"❌ Invalid date format: {iso_str}. Use ISO 8601 (e.g., 2024-01-01T00:00:00Z)")
            sys.exit(1)

    # Smart defaults if dates aren't provided
    start_dt = parse_date(args.start_date) or datetime.now(timezone.utc) - timedelta(days=7)
    end_dt = parse_date(args.end_date) or datetime.now(timezone.utc).replace(hour=23, minute=59, second=59)

    return args.channel_id, start_dt, end_dt

async def main():
    intents = discord.Intents.default()
    intents.message_content = True  # Required to read message text
    intents.guilds = True

    client = commands.Bot(command_prefix='!', intents=intents)
    await client.login(BOT_TOKEN)
    print(f"✅ Bot logged in as {client.user} (ID: {client.user.id})")

    channel_id, start_dt, end_dt = parse_args()

    if end_dt < start_dt:
        print("❌ Error: End date must be after start date.")
        return

    channel = await client.fetch_channel(channel_id)
    if not channel:
        print(f"❌ Channel with ID {channel_id} not found or bot lacks access.")
        return

    print(f"\n📥 Fetching messages from '{channel.name}' (ID: {channel.id})...")
    print(f"   Range: {start_dt.strftime('%Y-%m-%d %H:%M:%S UTC')} → {end_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    with open("discord_messages.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "author_id", "username", "content", "channel_id"])
        writer.writeheader()

        count = 0
        # discord.py automatically paginates within the API's history limit
        async for message in channel.history(before=end_dt, after=start_dt):
            try:
                row = {
                    "timestamp": message.created_at.isoformat(),
                    "author_id": message.author.id,
                    "username": message.author.name,
                    "content": message.content or "(deleted/NSFW)",
                    "channel_id": channel.id
                }
                writer.writerow(row)
                count += 1

                # Respect Discord's rate limits (~5 req/sec per endpoint)
                if count % 50 == 0:
                    await asyncio.sleep(0.6)

            except discord.Forbidden:
                print("⚠️ Access denied to channel.")
                break
            except Exception as e:
                print(f"❌ Error processing message {message.id}: {e}")

        print(f"\n✅ Done! Fetched {count} messages saved to 'discord_messages.csv'")

        await client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user.")
