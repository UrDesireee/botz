import discord
import os
import requests
import pytz  # New import for timezone handling
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

# Read Token from Environment Variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Intents setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="/", intents=intents)

# Timezone Setup (Server is GMT+1, but you want GMT+0)
SERVER_TZ = pytz.timezone("Europe/Warsaw")  # Assuming Railway is using Warsaw time
CORRECT_TZ = pytz.timezone("Etc/GMT")  # Your actual timezone (GMT+0)

# Function to fetch prayer times
def get_prayer_times(city, country):
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2"
    response = requests.get(url)
    data = response.json()
    fajr = data["data"]["timings"]["Fajr"]
    maghrib = data["data"]["timings"]["Maghrib"]

    # Convert to UTC then adjust to GMT+0
    fajr_time = datetime.strptime(fajr, "%H:%M").replace(tzinfo=SERVER_TZ).astimezone(CORRECT_TZ).strftime("%H:%M")
    maghrib_time = datetime.strptime(maghrib, "%H:%M").replace(tzinfo=SERVER_TZ).astimezone(CORRECT_TZ).strftime("%H:%M")

    return fajr_time, maghrib_time

# Scheduler setup
scheduler = AsyncIOScheduler()

# Function to send prayer messages
async def send_prayer_message(city, country, user_id, guild_id):
    fajr_time, maghrib_time = get_prayer_times(city, country)

    now = datetime.now(CORRECT_TZ).strftime("%H:%M")  # Get current time in GMT+0

    guild = bot.get_guild(guild_id)
    if not guild or guild_id not in prayer_channels:
        return
    
    channel = bot.get_channel(prayer_channels[guild_id])
    
    if not channel:
        return

    if now == fajr_time:
        title = "🌙 Fajr Time 🌙"
        color = discord.Color.blue()
        prayer_time = fajr_time
        emoji = "🕌"
    elif now == maghrib_time:
        title = "🌅 Maghrib Time 🌅"
        color = discord.Color.orange()
        prayer_time = maghrib_time
        emoji = "🌇"
    else:
        return  # If it's not Fajr or Maghrib, do nothing

    # Create an embed message
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="🕒 Current Time", value=f"`{now}`", inline=True)
    embed.add_field(name="📍 Location", value=f"{city}, {country}", inline=True)
    embed.add_field(name="⏳ Prayer Time", value=f"`{prayer_time}`", inline=True)
    
    await channel.send(f"{emoji} {user_id}, it's time for prayer!", embed=embed)

# Function to schedule prayer announcements correctly
def schedule_prayer_updates():
    scheduler.add_job(send_prayer_message, "cron", hour="*", minute="*", args=("Warsaw", "Poland", 1231967004894953513, 1285310396416397415), timezone=CORRECT_TZ)
    scheduler.add_job(send_prayer_message, "cron", hour="*", minute="*", args=("ReggioEmilia", "Italy", 816786360693555251, 1285310396416397415), timezone=CORRECT_TZ)
    scheduler.start()

# Start event
@bot.event
async def on_ready():
    print(f"{bot.user} has connected!")
    schedule_prayer_updates()

# Run the bot
bot.run(TOKEN)
