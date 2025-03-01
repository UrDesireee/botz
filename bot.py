import discord
import requests
import asyncio
from discord.ext import commands
from datetime import datetime, date
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

# ✅ Convert to local time for Reggio Emilia & Warsaw
def convert_to_local_time(prayer_time: str, city: str):
    fmt = "%H:%M"
    utc_now = datetime.utcnow()

    # Convert prayer time string to UTC-based datetime
    prayer_time_utc = datetime.strptime(prayer_time, fmt).replace(
        year=utc_now.year, month=utc_now.month, day=utc_now.day
    )

    # Assign correct timezone
    if city.lower() == "reggio emilia":
        tz = ZoneInfo("Europe/Rome") if "ZoneInfo" in globals() else timezone("Europe/Rome")
    elif city.lower() == "warsaw":
        tz = ZoneInfo("Europe/Warsaw") if "ZoneInfo" in globals() else timezone("Europe/Warsaw")
    else:
        return prayer_time_utc  # Fallback to UTC if city is unknown

    # Convert to local time
    return tz.localize(prayer_time_utc) if "ZoneInfo" not in globals() else prayer_time_utc.replace(tzinfo=tz)

# ✅ Command to set Italy prayer times channel
@bot.command(name="setupitaly")
async def setup_italy(ctx, channel_id: int):
    global channel_id_italy
    channel_id_italy = channel_id
    await ctx.send(f"✅ Italy prayer times channel set to <#{channel_id}>")

# ✅ Command to set Poland prayer times channel
@bot.command(name="setuppoland")
async def setup_poland(ctx, channel_id: int):
    global channel_id_poland
    channel_id_poland = channel_id
    await ctx.send(f"✅ Poland prayer times channel set to <#{channel_id}>")

# ✅ Background task to send prayer notifications
async def schedule_prayer_times():
    await bot.wait_until_ready()
    
    while True:
        today = date.today()
        fajr_italy, maghrib_italy = get_prayer_times("Reggio Emilia", "Italy")  # ✅ Changed to Reggio Emilia
        fajr_poland, maghrib_poland = get_prayer_times("Warsaw", "Poland")

        if not fajr_italy or not fajr_poland:
            await asyncio.sleep(60)
            continue

        # Convert fetched times to local timezone
        fajr_time_italy = convert_to_local_time(fajr_italy, "reggio emilia")
        maghrib_time_italy = convert_to_local_time(maghrib_italy, "reggio emilia")
        fajr_time_poland = convert_to_local_time(fajr_poland, "warsaw")
        maghrib_time_poland = convert_to_local_time(maghrib_poland, "warsaw")

        now = datetime.now(ZoneInfo("Europe/Rome") if "ZoneInfo" in globals() else timezone("Europe/Rome"))

        # Prepare events (sorted by soonest)
        events = [
            ("italy_fajr", (fajr_time_italy - now).total_seconds()),
            ("italy_maghrib", (maghrib_time_italy - now).total_seconds()),
            ("poland_fajr", (fajr_time_poland - now).total_seconds()),
            ("poland_maghrib", (maghrib_time_poland - now).total_seconds())
        ]
        events.sort(key=lambda x: x[1])

        # Process the closest prayer time event
        event, wait_time = events[0]
        await asyncio.sleep(wait_time)

        # Send message to the correct channel
        if event == "italy_fajr" and channel_id_italy:
            channel = bot.get_channel(channel_id_italy)
            if channel:
                await channel.send(f"☀️ **Fajr time** has arrived! <@816786360693555251>")
        elif event == "italy_maghrib" and channel_id_italy:
            channel = bot.get_channel(channel_id_italy)
            if channel:
                await channel.send(f"🌙 **Maghrib time** has arrived! <@816786360693555251>")
        elif event == "poland_fajr" and channel_id_poland:
            channel = bot.get_channel(channel_id_poland)
            if channel:
                await channel.send(f"☀️ **Fajr time** has arrived! <@1231967004894953513>")
        elif event == "poland_maghrib" and channel_id_poland:
            channel = bot.get_channel(channel_id_poland)
            if channel:
                await channel.send(f"🌙 **Maghrib time** has arrived! <@1231967004894953513>")

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
