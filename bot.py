import discord
import requests
import asyncio
from discord.ext import commands
from datetime import datetime, date
import os

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Channel IDs for Poland and Italy (set using bot commands)
channel_id_italy = None
channel_id_poland = None

# Function to fetch Fajr and Maghrib times from the Aladhan APIs
def get_prayer_times(city: str, country: str):
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}"
    try:
        response = requests.get(url)
        data = response.json()
        timings = data["data"]["timings"]
        fajr_time = timings["Fajr"]
        maghrib_time = timings["Maghrib"]
        return fajr_time, maghrib_time
    except Exception as e:
        print(f"Error fetching prayer times: {e}")
        return None, None

# Command to set Italy prayer channel
@bot.command(name="setupitaly")
async def setup_italy(ctx, channel_id: int):
    global channel_id_italy
    channel_id_italy = channel_id
    await ctx.send(f"✅ Italy prayer times channel set to <#{channel_id}>")

# Command to set Poland prayer channel
@bot.command(name="setuppoland")
async def setup_poland(ctx, channel_id: int):
    global channel_id_poland
    channel_id_poland = channel_id
    await ctx.send(f"✅ Poland prayer times channel set to <#{channel_id}>")

# Function to schedule and send prayer notifications
async def schedule_prayer_times():
    await bot.wait_until_ready()
    while True:
        today = date.today()
        fajr_italy, maghrib_italy = get_prayer_times("ReggioEmilia", "Italy")
        fajr_poland, maghrib_poland = get_prayer_times("Warsaw", "Poland")

        if not fajr_italy or not fajr_poland:
            await asyncio.sleep(60)
            continue

        fmt = "%H:%M"
        now = datetime.now()
        
        # Convert fetched times to datetime objects
        fajr_time_italy = datetime.strptime(fajr_italy, fmt).replace(year=today.year, month=today.month, day=today.day)
        maghrib_time_italy = datetime.strptime(maghrib_italy, fmt).replace(year=today.year, month=today.month, day=today.day)
        fajr_time_poland = datetime.strptime(fajr_poland, fmt).replace(year=today.year, month=today.month, day=today.day)
        maghrib_time_poland = datetime.strptime(maghrib_poland, fmt).replace(year=today.year, month=today.month, day=today.day)

        # Ensure scheduling for the next upcoming times
        if now > fajr_time_italy:
            fajr_time_italy = fajr_time_italy.replace(day=today.day + 1)
        if now > maghrib_time_italy:
            maghrib_time_italy = maghrib_time_italy.replace(day=today.day + 1)
        if now > fajr_time_poland:
            fajr_time_poland = fajr_time_poland.replace(day=today.day + 1)
        if now > maghrib_time_poland:
            maghrib_time_poland = maghrib_time_poland.replace(day=today.day + 1)

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

# Background task to check and send prayer notifications
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    asyncio.create_task(schedule_prayer_times())  # Use asyncio.create_task instead


# Run the bot
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Bot token is missing! Set DISCORD_BOT_TOKEN as an environment variable.")
bot.run(TOKEN)

