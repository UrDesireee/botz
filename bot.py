import discord
import os
import requests
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Read Token from Railway Environment Variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Intents setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store the prayer announcement channel per server
prayer_channels = {}

# User IDs for pinging
user_poland = "<@1231967004894953513>"
user_italy = "<@816786360693555251>"

# Function to fetch prayer times **WITHOUT EXTRA TIMEZONE CONVERSION**
def get_prayer_times(city, country):
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=3"  # MWL method
    response = requests.get(url)
    data = response.json()
    
    fajr_time = data["data"]["timings"]["Fajr"]  # Already in local time
    maghrib_time = data["data"]["timings"]["Maghrib"]  # Already in local time

    return fajr_time, maghrib_time

# Function to send prayer messages
async def send_prayer_message(city, country, user_id, guild_id):
    fajr_time, maghrib_time = get_prayer_times(city, country)
    
    now = datetime.now().strftime("%H:%M")  # Get current time in local format

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
        return

    # Create an embed message
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="🕒 Current Time", value=f"`{now}`", inline=True)
    embed.add_field(name="📍 Location", value=f"{city}, {country}", inline=True)
    embed.add_field(name="⏳ Prayer Time", value=f"`{prayer_time}`", inline=True)
    
    await channel.send(f"{emoji} {user_id}, it's time for prayer!", embed=embed)

# Function to schedule prayer announcements correctly
def schedule_prayer_updates():
    scheduler = AsyncIOScheduler()
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
    fajr_poland, maghrib_poland = get_prayer_times("Warsaw", "Poland")
    fajr_italy, maghrib_italy = get_prayer_times("ReggioEmilia", "Italy")

    # Create an embed message
    embed = discord.Embed(title="🕌 Today's Prayer Times 🕌", color=discord.Color.green())
    
    embed.add_field(name="📍 **Warsaw, Poland**", value=f"🌙 Fajr: `{fajr_poland}`\n🌅 Maghrib: `{maghrib_poland}`", inline=False)
    embed.add_field(name="📍 **Reggio Emilia, Italy**", value=f"🌙 Fajr: `{fajr_italy}`\n🌅 Maghrib: `{maghrib_italy}`", inline=False)
    
    embed.set_footer(text="Prayer times are based on the Muslim World League (MWL) method.")

    await ctx.send(embed=embed)

# Start event
@bot.event
async def on_ready():
    print(f"{bot.user} has connected!")
    schedule_prayer_updates()

# Run the bot
bot.run(TOKEN)
