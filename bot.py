import discord
from discord.ext import commands, tasks
import requests
import datetime
import os
import pytz
import asyncio

# Bot configuration
TOKEN = os.environ.get('DISCORD_TOKEN')  # Discord bot token
CHANNEL_ID = int(os.environ.get('CHANNEL_ID'))  # Channel ID where messages will be sent
REGGIO_USER_ID = 816786360693555251  # User ID to ping for Reggio Emilia
WARSAW_USER_ID = 1231967004894953513  # User ID to ping for Warsaw

# Prayer API configuration
PRAYER_API_URL = "http://api.aladhan.com/v1/timingsByCity"

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# City information
cities = {
    "reggio": {
        "name": "Reggio Emilia, Italy",
        "country": "Italy",
        "timezone": "Europe/Rome",
        "user_id": REGGIO_USER_ID,
        "last_notified_date": None,
        "prayers_notified": {"Fajr": False, "Maghrib": False},
        "emoji": "🇮🇹"
    },
    "warsaw": {
        "name": "Warsaw, Poland",
        "country": "Poland",
        "timezone": "Europe/Warsaw",
        "user_id": WARSAW_USER_ID,
        "last_notified_date": None,
        "prayers_notified": {"Fajr": False, "Maghrib": False},
        "emoji": "🇵🇱"
    }
}

# Prayer emojis
prayer_emojis = {
    "Fajr": "🌅",
    "Maghrib": "🕌"
}

# Function to get prayer times for a specific city
def get_prayer_times(city_name, country):
    params = {
        'city': city_name.split(',')[0],  # Extract just the city name
        'country': country,
        'method': 2  # ISNA calculation method
    }
    
    try:
        response = requests.get(PRAYER_API_URL, params=params)
        data = response.json()
        
        if response.status_code == 200 and data['code'] == 200:
            timings = data['data']['timings']
            date = data['data']['date']['gregorian']['date']
            return {
                "date": date,
                "Fajr": timings['Fajr'],
                "Maghrib": timings['Maghrib']
            }
        else:
            print(f"Error fetching prayer times: {data.get('status')}")
            return None
    except Exception as e:
        print(f"Error in API request: {e}")
        return None

# Reset notification flags when the day changes
def reset_notification_flags(city_key):
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    if cities[city_key]["last_notified_date"] != current_date:
        cities[city_key]["last_notified_date"] = current_date
        cities[city_key]["prayers_notified"] = {"Fajr": False, "Maghrib": False}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    check_prayer_times.start()

@tasks.loop(minutes=1)
async def check_prayer_times():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Channel with ID {CHANNEL_ID} not found.")
        return
    
    current_time = datetime.datetime.now(pytz.timezone('UTC'))
    
    for city_key, city_info in cities.items():
        # Reset notification flags if it's a new day
        reset_notification_flags(city_key)
        
        # Get prayer times for the city
        prayer_data = get_prayer_times(city_info["name"], city_info["country"])
        if not prayer_data:
            continue
        
        # Convert to city's timezone for comparison
        city_timezone = pytz.timezone(city_info["timezone"])
        city_current_time = current_time.astimezone(city_timezone)
        
        # Check each prayer time we're interested in
        for prayer in ["Fajr", "Maghrib"]:
            if cities[city_key]["prayers_notified"][prayer]:
                continue  # Skip if already notified today
            
            prayer_time_str = prayer_data[prayer]
            prayer_hour, prayer_minute = map(int, prayer_time_str.split(':'))
            
            # Create a datetime object for the prayer time
            prayer_datetime = city_current_time.replace(
                hour=prayer_hour, 
                minute=prayer_minute, 
                second=0, 
                microsecond=0
            )
            
            # Check if it's time to send the notification
            time_diff = (prayer_datetime - city_current_time).total_seconds() / 60
            
            if abs(time_diff) < 1:  # Within 1 minute
                user_to_ping = f"<@{city_info['user_id']}>"
                
                # Create fancy embedded message with emojis
                embed = discord.Embed(
                    title=f"{prayer_emojis[prayer]} {prayer} Time {prayer_emojis[prayer]}",
                    color=0x3498db if prayer == "Fajr" else 0x9b59b6
                )
                
                # Add fields with current time, location, and prayer time
                embed.add_field(
                    name="⏰ Current Time", 
                    value=city_current_time.strftime("%H:%M"), 
                    inline=True
                )
                embed.add_field(
                    name=f"📍 Location", 
                    value=city_info["name"], 
                    inline=True
                )
                embed.add_field(
                    name="⏳ Prayer Time", 
                    value=prayer_time_str, 
                    inline=True
                )
                
                # Add a colored line on the left (using embed color)
                await channel.send(f"{user_to_ping}, it's time for prayer!", embed=embed)
                cities[city_key]["prayers_notified"][prayer] = True
                print(f"Notification sent for {prayer} in {city_info['name']}")

@bot.command(name='gettime')
async def get_time(ctx):
    # Create a fancy embedded message with emojis
    embed = discord.Embed(
        title="🕌 Today's Prayer Times 🕌",
        color=0x2ecc71  # Green color for the embed
    )
    
    for city_key, city_info in cities.items():
        prayer_data = get_prayer_times(city_info["name"], city_info["country"])
        
        if prayer_data:
            # Add a field for each city with prayer times
            city_times = (
                f"{prayer_emojis['Fajr']} Fajr: {prayer_data['Fajr']}\n"
                f"{prayer_emojis['Maghrib']} Maghrib: {prayer_data['Maghrib']}"
            )
            
            embed.add_field(
                name=f"{city_info['emoji']} {city_info['name']}",
                value=city_times,
                inline=False
            )
        else:
            embed.add_field(
                name=f"{city_info['emoji']} {city_info['name']}",
                value="Could not fetch prayer times.",
                inline=False
            )
    
    await ctx.send(embed=embed)

# Run the bot
bot.run(TOKEN)