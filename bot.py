import discord
import requests
import asyncio
import os
from discord.ext import commands, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

# Bot token (Replace with your actual bot token)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")


# Dictionary to store the prayer channel
prayer_channels = {}

# User IDs to ping
user_poland = "<@1231967004894953513>"
user_italy = "<@816786360693555251>"

# Timezone Offset (Adjust for Server Time: GMT+1)
TIMEZONE_OFFSET = 1

# Intents setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Change the TIMEZONE_OFFSET to -1 to correct for your actual timezone
TIMEZONE_OFFSET = 0  

# Function to fetch prayer times and adjust to your timezone
def get_prayer_times(city, country):
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2"
    response = requests.get(url)
    data = response.json()
    fajr = data["data"]["timings"]["Fajr"]
    maghrib = data["data"]["timings"]["Maghrib"]

    # Convert times to match your actual timezone
    fajr_time = (datetime.strptime(fajr, "%H:%M") + timedelta(hours=TIMEZONE_OFFSET)).strftime("%H:%M")
    maghrib_time = (datetime.strptime(maghrib, "%H:%M") + timedelta(hours=TIMEZONE_OFFSET)).strftime("%H:%M")

    return fajr_time, maghrib_time


# Scheduler setup
scheduler = AsyncIOScheduler()

# Function to send prayer messages
async def send_prayer_message(city, country, user_id, guild_id):
    fajr_time, maghrib_time = get_prayer_times(city, country)

    now = datetime.now().strftime("%H:%M")

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

# Function to schedule prayer announcements
def schedule_prayer_updates():
    scheduler.add_job(send_prayer_message, "cron", hour="*", minute="*", args=("Warsaw", "Poland", user_poland, 1285310396416397415))
    scheduler.add_job(send_prayer_message, "cron", hour="*", minute="*", args=("Reggio Emilia", "Italy", user_italy, 1285310396416397415))
    scheduler.start()

# Command to set the announcement channel
@bot.command()
async def setupchannel(ctx, channel_id: int):
    prayer_channels[ctx.guild.id] = channel_id
    await ctx.send(f"✅ Prayer announcements will be sent to <#{channel_id}>")

# Command to get today's Fajr and Maghrib times
@bot.command()
async def gettime(ctx):
    # Get prayer times for both locations
    fajr_poland, maghrib_poland = get_prayer_times("Warsaw", "Poland")
    fajr_italy, maghrib_italy = get_prayer_times("Reggio Emilia", "Italy")

    # Create an embed message
    embed = discord.Embed(title="🕌 Today's Prayer Times 🕌", color=discord.Color.green())
    
    embed.add_field(name="📍 **Warsaw, Poland**", value=f"🌙 Fajr: `{fajr_poland}`\n🌅 Maghrib: `{maghrib_poland}`", inline=False)
    embed.add_field(name="📍 **Reggio Emilia, Italy**", value=f"🌙 Fajr: `{fajr_italy}`\n🌅 Maghrib: `{maghrib_italy}`", inline=False)
    
    embed.set_footer(text="Prayer times are adjusted for your timezone (GMT+1).")

    await ctx.send(embed=embed)

# Start event
@bot.event
async def on_ready():
    print(f"{bot.user} has connected!")
    schedule_prayer_updates()

# Run the bot
bot.run(TOKEN)
