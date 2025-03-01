import discord
import requests
import asyncio
from discord.ext import commands
from datetime import datetime, date, UTC
import os

# ✅ Fix for time zones
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    from pytz import timezone  # For Python 3.8 and below

# ✅ Enable intents
intents = discord.Intents.default()
intents.message_content = True  

# ✅ Set up bot with command prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ Global channel variables
channel_id_italy = None
channel_id_poland = None

# ✅ Track sent messages to prevent spam
sent_messages = {
    "italy_fajr": False,
    "italy_maghrib": False,
    "poland_fajr": False,
    "poland_maghrib": False
}

# ✅ Function to fetch prayer times
def get_prayer_times(city: str, country: str):
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}"
    try:
        response = requests.get(url)
        data = response.json()
        timings = data["data"]["timings"]
        return timings["Fajr"], timings["Maghrib"]
    except Exception as e:
        print(f"Error fetching prayer times: {e}")
        return None, None

# ✅ Convert to local time for ReggioEmilia & Warsaw
def convert_to_local_time(prayer_time: str, city: str):
    fmt = "%H:%M"
    utc_now = datetime.now(UTC)  # ✅ Updated: Correct timezone-aware datetime

    # Convert prayer time string to UTC-based datetime
    prayer_time_utc = datetime.strptime(prayer_time, fmt).replace(
        year=utc_now.year, month=utc_now.month, day=utc_now.day, tzinfo=UTC
    )

    # Assign correct timezone
    if city.lower() == "reggioemilia":
        tz = ZoneInfo("Europe/Rome") if "ZoneInfo" in globals() else timezone("Europe/Rome")
    elif city.lower() == "warsaw":
        tz = ZoneInfo("Europe/Warsaw") if "ZoneInfo" in globals() else timezone("Europe/Warsaw")
    else:
        return prayer_time_utc  # Fallback to UTC if city is unknown

    # Convert to local time
    return prayer_time_utc.astimezone(tz)

# ✅ Command to set Italy prayer times channel
@bot.command(name="setupitaly")
async def setup_italy(ctx, channel_id: int):
    global channel_id_italy
    channel_id_italy = channel_id
    await ctx.send(f"✅ Italy (ReggioEmilia) prayer times channel set to <#{channel_id}>")

# ✅ Command to set Poland prayer times channel
@bot.command(name="setuppoland")
async def setup_poland(ctx, channel_id: int):
    global channel_id_poland
    channel_id_poland = channel_id
    await ctx.send(f"✅ Poland (Warsaw) prayer times channel set to <#{channel_id}>")

# ✅ Background task to send prayer notifications
async def schedule_prayer_times():
    await bot.wait_until_ready()
    
    while True:
        today = date.today()
        fajr_italy, maghrib_italy = get_prayer_times("ReggioEmilia", "Italy")  # ✅ Changed to "ReggioEmilia"
        fajr_poland, maghrib_poland = get_prayer_times("Warsaw", "Poland")

        if not fajr_italy or not fajr_poland:
            await asyncio.sleep(60)
            continue

        # Convert fetched times to local timezone
        fajr_time_italy = convert_to_local_time(fajr_italy, "reggioemilia")
        maghrib_time_italy = convert_to_local_time(maghrib_italy, "reggioemilia")
        fajr_time_poland = convert_to_local_time(fajr_poland, "warsaw")
        maghrib_time_poland = convert_to_local_time(maghrib_poland, "warsaw")

        now = datetime.now(ZoneInfo("Europe/Rome") if "ZoneInfo" in globals() else timezone("Europe/Rome"))

        # ✅ Check if it's exactly prayer time and send message once per day
        if now >= fajr_time_italy and not sent_messages["italy_fajr"]:
            if channel_id_italy:
                channel = bot.get_channel(channel_id_italy)
                if channel:
                    await channel.send(f"☀️ **Fajr time** has arrived in ReggioEmilia! <@816786360693555251>")
                    sent_messages["italy_fajr"] = True

        if now >= maghrib_time_italy and not sent_messages["italy_maghrib"]:
            if channel_id_italy:
                channel = bot.get_channel(channel_id_italy)
                if channel:
                    await channel.send(f"🌙 **Maghrib time** has arrived in ReggioEmilia! <@816786360693555251>")
                    sent_messages["italy_maghrib"] = True

        if now >= fajr_time_poland and not sent_messages["poland_fajr"]:
            if channel_id_poland:
                channel = bot.get_channel(channel_id_poland)
                if channel:
                    await channel.send(f"☀️ **Fajr time** has arrived in Warsaw! <@1231967004894953513>")
                    sent_messages["poland_fajr"] = True

        if now >= maghrib_time_poland and not sent_messages["poland_maghrib"]:
            if channel_id_poland:
                channel = bot.get_channel(channel_id_poland)
                if channel:
                    await channel.send(f"🌙 **Maghrib time** has arrived in Warsaw! <@1231967004894953513>")
                    sent_messages["poland_maghrib"] = True

        # ✅ Reset sent message flags at midnight
        if now.hour == 0 and now.minute == 0:
            sent_messages["italy_fajr"] = False
            sent_messages["italy_maghrib"] = False
            sent_messages["poland_fajr"] = False
            sent_messages["poland_maghrib"] = False
            print("✅ Reset sent message flags for the new day")

        # ✅ Sleep for 30 seconds before checking again
        await asyncio.sleep(30)

# ✅ Start background task when bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    asyncio.create_task(schedule_prayer_times())

# ✅ Run the bot securely
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("🚨 Bot token is missing! Set DISCORD_BOT_TOKEN as an environment variable.")

bot.run(TOKEN)
