import discord
from discord.ext import commands, tasks
import requests
import datetime
import os
import pytz
import time

class PrayerTimesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Bot configuration
        self.CHANNEL_ID = int(os.environ.get('CHANNEL_ID'))  # Channel ID where messages will be sent
        self.REGGIO_USER_ID = 816786360693555251  # User ID to ping for Reggio Emilia
        self.WARSAW_USER_ID = 1231967004894953513  # User ID to ping for Warsaw
        
        # Prayer API configuration
        self.PRAYER_API_URL = "http://api.aladhan.com/v1/timingsByCity"
        
        # Animated emoji IDs
        self.animated_emojis = {
            "99": "1304880064160338021",  # Your provided animated emoji
            "fajr": "EMOJI_ID_HERE",      # Placeholder - replace with actual ID
            "maghrib": "EMOJI_ID_HERE",   # Placeholder - replace with actual ID
            "clock": "EMOJI_ID_HERE",     # Placeholder - replace with actual ID
            "location": "EMOJI_ID_HERE",  # Placeholder - replace with actual ID
            "prayer": "EMOJI_ID_HERE"     # Placeholder - replace with actual ID
        }
        
        # City information
        self.cities = {
            "reggio": {
                "name": "Reggio Emilia",
                "country": "Italy",
                "timezone": "Europe/Rome",
                "user_id": self.REGGIO_USER_ID,
                "last_notified_date": None,
                "prayers_notified": {"Fajr": False, "Maghrib": False},
                "emoji": "🇮🇹"
            },
            "warsaw": {
                "name": "Warsaw",
                "country": "Poland",
                "timezone": "Europe/Warsaw",
                "user_id": self.WARSAW_USER_ID,
                "last_notified_date": None,
                "prayers_notified": {"Fajr": False, "Maghrib": False},
                "emoji": "🇵🇱"
            }
        }
        
        # Prayer emojis and colors
        self.prayer_info = {
            "Fajr": {
                "emoji": "🌅",  # Fallback regular emoji
                "animated_emoji_key": "fajr",  # Key for the animated emoji in the dictionary
                "color": 0x48C9B0  # Teal
            },
            "Maghrib": {
                "emoji": "🕌",  # Fallback regular emoji
                "animated_emoji_key": "maghrib",  # Key for the animated emoji in the dictionary
                "color": 0x9B59B6  # Purple
            }
        }
        
        # Start the task when the cog is initialized
        self.check_prayer_times.start()
    
    def cog_unload(self):
        # Stop the task when the cog is unloaded
        self.check_prayer_times.cancel()
    
    # Helper function to get animated emoji or fallback to regular emoji
    def get_emoji(self, key, fallback=""):
        if key in self.animated_emojis and self.animated_emojis[key] != "EMOJI_ID_HERE":
            return f"<a:{key}:{self.animated_emojis[key]}>"
        return fallback
    
    # Function to get prayer times for a specific city
    def get_prayer_times(self, city_name, country):
        params = {
            'city': city_name,
            'country': country,
            'method': 3  # ISNA calculation method
        }
        
        try:
            response = requests.get(self.PRAYER_API_URL, params=params)
            data = response.json()
            
            if response.status_code == 200 and data['code'] == 200:
                timings = data['data']['timings']
                date = data['data']['date']['gregorian']['date']
                return {
                    "date": date,
                    "Fajr": timings['Fajr'],
                    "Maghrib": timings['Maghrib'],
                    "timestamp": data['data']['date']['timestamp']
                }
            else:
                print(f"Error fetching prayer times: {data.get('status')}")
                return None
        except Exception as e:
            print(f"Error in API request: {e}")
            return None
    
    # Function to convert HH:MM to Unix timestamp for a given date and timezone
    def time_to_timestamp(self, time_str, date_str, timezone_str):
        # Parse the date and time
        hour, minute = map(int, time_str.split(':'))
        day, month, year = map(int, date_str.split('-'))
        
        # Create a datetime object in the specified timezone
        tz = pytz.timezone(timezone_str)
        dt = datetime.datetime(year, month, day, hour, minute, 0, tzinfo=tz)
        
        # Convert to Unix timestamp (seconds since epoch)
        return int(dt.timestamp())
    
    # Reset notification flags when the day changes
    def reset_notification_flags(self, city_key):
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        if self.cities[city_key]["last_notified_date"] != current_date:
            self.cities[city_key]["last_notified_date"] = current_date
            self.cities[city_key]["prayers_notified"] = {"Fajr": False, "Maghrib": False}
    
    @tasks.loop(minutes=1)
    async def check_prayer_times(self):
        channel = self.bot.get_channel(self.CHANNEL_ID)
        if not channel:
            print(f"Channel with ID {self.CHANNEL_ID} not found.")
            return
        
        current_time = datetime.datetime.now(pytz.timezone('UTC'))
        
        for city_key, city_info in self.cities.items():
            # Reset notification flags if it's a new day
            self.reset_notification_flags(city_key)
            
            # Get prayer times for the city
            prayer_data = self.get_prayer_times(city_info["name"], city_info["country"])
            if not prayer_data:
                continue
            
            # Convert to city's timezone for comparison
            city_timezone = pytz.timezone(city_info["timezone"])
            city_current_time = current_time.astimezone(city_timezone)
            
            # Check each prayer time we're interested in
            for prayer in ["Fajr", "Maghrib"]:
                if self.cities[city_key]["prayers_notified"][prayer]:
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
                    
                    # Get Unix timestamps for Discord timestamp formatting
                    current_timestamp = int(city_current_time.timestamp())
                    prayer_timestamp = self.time_to_timestamp(prayer_time_str, prayer_data["date"], city_info["timezone"])
                    
                    # Get animated emoji or fallback to regular
                    prayer_emoji = self.get_emoji(self.prayer_info[prayer]["animated_emoji_key"], self.prayer_info[prayer]["emoji"])
                    clock_emoji = self.get_emoji("clock", "⏰")
                    location_emoji = self.get_emoji("location", "📍")
                    prayer_time_emoji = self.get_emoji("prayer", "⏳")
                    test_emoji = self.get_emoji("99", "")  # Using your provided emoji
                    
                    # Create a cleanly formatted embedded message
                    embed = discord.Embed(
                        description=f"**{prayer_emoji} {prayer} Time {prayer_emoji}**",
                        color=self.prayer_info[prayer]['color']
                    )
                    
                    # Add location and time with Discord timestamp format
                    embed.add_field(
                        name="",
                        value=f"{clock_emoji} **Current Time:** <t:{current_timestamp}:t>\n"
                             f"{location_emoji} **Location:** {city_info['emoji']} {city_info['name']}, {city_info['country']}\n"
                             f"{prayer_time_emoji} **Prayer Time:** <t:{prayer_timestamp}:t>\n"
                             f"{test_emoji} Using your provided emoji",
                        inline=False
                    )
                    
                    # Add a nice footer with the date
                    embed.set_footer(text=f"Date: {prayer_data['date']}")
                    
                    await channel.send(f"{user_to_ping}, it's time for prayer!", embed=embed)
                    self.cities[city_key]["prayers_notified"][prayer] = True
                    print(f"Notification sent for {prayer} in {city_info['name']}")
    
    @check_prayer_times.before_loop
    async def before_check_prayer_times(self):
        await self.bot.wait_until_ready()
    
    @commands.command(name='gettime')
    async def get_time(self, ctx):
        # Create a cleaner, more spaced out embed
        embed = discord.Embed(
            title=f"{self.get_emoji('99', '🕌')} Today's Prayer Times {self.get_emoji('99', '🕌')}",
            color=0x2ecc71,  # Green color
            description="Prayer times for your locations today:"
        )
        
        for city_key, city_info in self.cities.items():
            prayer_data = self.get_prayer_times(city_info["name"], city_info["country"])
            
            if prayer_data:
                # Get Unix timestamps for prayer times
                fajr_timestamp = self.time_to_timestamp(prayer_data["Fajr"], prayer_data["date"], city_info["timezone"])
                maghrib_timestamp = self.time_to_timestamp(prayer_data["Maghrib"], prayer_data["date"], city_info["timezone"])
                
                # Get animated emojis for each prayer
                fajr_emoji = self.get_emoji(self.prayer_info["Fajr"]["animated_emoji_key"], self.prayer_info["Fajr"]["emoji"])
                maghrib_emoji = self.get_emoji(self.prayer_info["Maghrib"]["animated_emoji_key"], self.prayer_info["Maghrib"]["emoji"])
                
                # Format each city's prayer times with Discord timestamp format
                embed.add_field(
                    name=f"\n{city_info['emoji']} **{city_info['name']}, {city_info['country']}**",
                    value=f"**Date:** {prayer_data['date']}\n\n"
                         f"{fajr_emoji} **Fajr:** <t:{fajr_timestamp}:t>\n\n"
                         f"{maghrib_emoji} **Maghrib:** <t:{maghrib_timestamp}:t>\n\n"
                         f"{self.get_emoji('99', '')}\n\u200B",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{city_info['emoji']} {city_info['name']}, {city_info['country']}",
                    value="Could not fetch prayer times.\n\u200B",
                    inline=False
                )
        
        # Add a helpful footer
        embed.set_footer(text="Use !gettime to view today's prayer times • Times shown in your local timezone")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PrayerTimesCog(bot))