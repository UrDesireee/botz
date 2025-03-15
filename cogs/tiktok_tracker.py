import discord
import asyncio
import requests
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import pytz
from bs4 import BeautifulSoup
import re

class TikTokTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CHANNEL_ID = 1350502449819156500
        self.TIKTOK_ACCOUNTS = {
            'ourdesiree': {
                'url': 'https://www.tiktok.com/@ourdesiree',
                'name': 'Desi',
                'initial_followers': 5,
                'initial_likes': 2485,
                'image_url': 'https://p16-pu-sign-no.tiktokcdn-eu.com/tos-no1a-avt-0068c001-no/68e1ce84651df415b90fc7f913ae6bd2~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=10399&refresh_token=c04f5428&x-expires=1742230800&x-signature=Yd92D900uBeTU5uj3OjnpphdC3g%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=no1a'  # Replace with actual image URL
            },
            'kawaii.style': {
                'url': 'https://www.tiktok.com/@kawaii.style',
                'name': 'Bunny',
                'initial_followers': 1,
                'initial_likes': 10,
                'image_url': 'https://p16-pu-sign-no.tiktokcdn-eu.com/tos-no1a-avt-0068c001-no/a9c500d07d08b141b806b33ac6f70a61~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=10399&refresh_token=a3cbaa28&x-expires=1742230800&x-signature=%2FJHbSLe%2BNPK7EpDOa9tNpiPME1w%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=no1a'  # Replace with actual image URL
            }
        }
        self.CHALLENGE_END = datetime(2025, 3, 22, 17, 0, 0, tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone('Etc/GMT-1'))
        self.POINTS_PER_LIKE = 1
        self.POINTS_PER_FOLLOWER = 20
        
        # Start the daily report task when the cog is loaded
        self.daily_report.start()
    
    def cog_unload(self):
        # Stop the task when the cog is unloaded
        self.daily_report.cancel()
    
    # Function to extract follower and like counts from TikTok profile
    async def get_tiktok_stats(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the script containing the data
            scripts = soup.find_all('script')
            data_script = None
            for script in scripts:
                if script.string and '"followerCount":' in script.string:
                    data_script = script.string
                    break
            
            if data_script:
                # Extract follower count
                follower_match = re.search(r'"followerCount":(\d+)', data_script)
                followers = int(follower_match.group(1)) if follower_match else 0
                
                # Extract like count
                like_match = re.search(r'"heartCount":(\d+)', data_script)
                likes = int(like_match.group(1)) if like_match else 0
                
                return followers, likes
            else:
                # Fallback to HTML parsing if script method fails
                followers_element = soup.select_one('strong[data-e2e="followers-count"]')
                likes_element = soup.select_one('strong[data-e2e="likes-count"]')
                
                followers = int(followers_element.get_text().replace(',', '')) if followers_element else 0
                likes = int(likes_element.get_text().replace(',', '')) if likes_element else 0
                
                return followers, likes
        except Exception as e:
            print(f"Error fetching TikTok stats: {e}")
            return 0, 0

    # Calculate points
    def calculate_points(self, followers, likes, initial_followers, initial_likes):
        new_followers = max(0, followers - initial_followers)
        new_likes = max(0, likes - initial_likes)
        
        return (new_followers * self.POINTS_PER_FOLLOWER) + (new_likes * self.POINTS_PER_LIKE)

    # Create embed for challenge status
    def create_status_embed(self, stats):
        # Determine who's leading
        desi_points = stats['ourdesiree']['points']
        bunny_points = stats['kawaii.style']['points']
        
        if desi_points > bunny_points:
            leader = 'ourdesiree'
            title = "Desi has more Points!!"
            color = discord.Color.purple()
        elif bunny_points > desi_points:
            leader = 'kawaii.style'
            title = "Bunny has more Points!!"
            color = discord.Color.pink()
        else:
            leader = None
            title = "It's a tie!"
            color = discord.Color.gold()
        
        embed = discord.Embed(
            title=title,
            description=f"TikTok Challenge Status - {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M UTC')}",
            color=color
        )
        
        # Add time remaining
        now = datetime.now(pytz.UTC).astimezone(self.CHALLENGE_END.tzinfo)
        if now < self.CHALLENGE_END:
            time_remaining = self.CHALLENGE_END - now
            days, remainder = divmod(time_remaining.total_seconds(), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, _ = divmod(remainder, 60)
            embed.add_field(
                name="Time Remaining",
                value=f"{int(days)}d {int(hours)}h {int(minutes)}m",
                inline=False
            )
        else:
            embed.add_field(
                name="Challenge Status",
                value="Challenge has ended!",
                inline=False
            )
        
        # Add stats for each account
        for username, data in stats.items():
            account_info = self.TIKTOK_ACCOUNTS[username]
            embed.add_field(
                name=f"{account_info['name']} (@{username})",
                value=f"**Points:** {data['points']}\n"
                      f"**New Followers:** +{data['followers'] - account_info['initial_followers']} ({data['followers']} total)\n"
                      f"**New Likes:** +{data['likes'] - account_info['initial_likes']} ({data['likes']} total)",
                inline=True
            )
        
        # Add comparison
        if leader:
            lead_amount = abs(desi_points - bunny_points)
            trailing = 'kawaii.style' if leader == 'ourdesiree' else 'ourdesiree'
            embed.add_field(
                name="Comparison",
                value=f"{self.TIKTOK_ACCOUNTS[leader]['name']} is leading by {lead_amount} points over {self.TIKTOK_ACCOUNTS[trailing]['name']}!",
                inline=False
            )
        
        # Set thumbnail to leader's image
        if leader:
            embed.set_thumbnail(url=self.TIKTOK_ACCOUNTS[leader]['image_url'])
        
        embed.set_footer(text="Points: 1 like = 1 point | 1 follower = 20 points")
        return embed

    @tasks.loop(time=time(hour=10, tzinfo=pytz.UTC))
    async def daily_report(self):
        channel = self.bot.get_channel(self.CHANNEL_ID)
        if not channel:
            print(f"Channel with ID {self.CHANNEL_ID} not found.")
            return
        
        stats = {}
        for username, account_data in self.TIKTOK_ACCOUNTS.items():
            followers, likes = await self.get_tiktok_stats(account_data['url'])
            points = self.calculate_points(followers, likes, account_data['initial_followers'], account_data['initial_likes'])
            
            stats[username] = {
                'followers': followers,
                'likes': likes,
                'points': points
            }
        
        embed = self.create_status_embed(stats)
        await channel.send(embed=embed)

    @daily_report.before_loop
    async def before_daily_report(self):
        await self.bot.wait_until_ready()

    @commands.command(name='tiktok')
    async def tiktok_command(self, ctx):
        if ctx.channel.id != self.CHANNEL_ID:
            await ctx.send("This command can only be used in the designated challenge channel.")
            return
        
        stats = {}
        for username, account_data in self.TIKTOK_ACCOUNTS.items():
            followers, likes = await self.get_tiktok_stats(account_data['url'])
            points = self.calculate_points(followers, likes, account_data['initial_followers'], account_data['initial_likes'])
            
            stats[username] = {
                'followers': followers,
                'likes': likes,
                'points': points
            }
        
        embed = self.create_status_embed(stats)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TikTokTracker(bot))