import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

class TikTokTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tiktok_username = "bunny_desiree"
        
        # Goals dictionary for Followers and Likes
        self.goals = {
            "Followers": [
                {"current": 0, "total": 100, "description": "First Hundred Followers"},
                {"current": 0, "total": 1000, "description": "First Thousand Followers"},
                {"current": 0, "total": 10000, "description": "Ten Thousand Followers"},
                {"current": 0, "total": 100000, "description": "Hundred Thousand Followers"},
                {"current": 0, "total": 1000000, "description": "One Million Followers"},
            ],
            "Likes": [
                {"current": 0, "total": 100, "description": "First Hundred Likes"},
                {"current": 0, "total": 1000, "description": "First Thousand Likes"},
                {"current": 0, "total": 10000, "description": "Ten Thousand Likes"},
                {"current": 0, "total": 100000, "description": "Hundred Thousand Likes"},
                {"current": 0, "total": 1000000, "description": "One Million Likes"},
            ]
        }
    
    def fetch_tiktok_stats_web(self):
        """Fetch TikTok stats using web scraping"""
        try:
            url = f"https://www.tiktok.com/@{self.tiktok_username}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            print(f"[DEBUG] Fetching TikTok page: {url} - Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print("[ERROR] Failed to fetch page, possible TikTok restrictions.")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            followers_elem = soup.find('strong', {'title': 'Followers'})
            likes_elem = soup.find('strong', {'title': 'Likes'})
            
            if not followers_elem or not likes_elem:
                print("[ERROR] Could not find followers or likes elements on TikTok profile page.")
                return None
            
            followers = self._clean_number(followers_elem.text)
            likes = self._clean_number(likes_elem.text)
            
            print(f"[DEBUG] Followers: {followers}, Likes: {likes}")
            
            return {"followers": followers, "likes": likes}
        
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Network Error: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return None
    
    def _clean_number(self, number_str):
        """Converts TikTok number string to integer."""
        try:
            cleaned = ''.join(char for char in number_str if char.isdigit() or char == '.')
            
            if 'K' in number_str:
                return int(float(cleaned) * 1000)
            elif 'M' in number_str:
                return int(float(cleaned) * 1000000)
            elif 'B' in number_str:
                return int(float(cleaned) * 1000000000)
            return int(float(cleaned))
        except ValueError:
            print(f"[ERROR] Could not convert {number_str} to number")
            return 0
    
    @commands.command(name="tiktok")
    async def tiktok_stats(self, ctx):
        """Command to display TikTok stats with web scraping"""
        await ctx.trigger_typing()
        
        stats = self.fetch_tiktok_stats_web()
        
        if stats:
            embed = discord.Embed(
                title=f"📊 TikTok Stats for @{self.tiktok_username}",
                color=discord.Color.blue()
            )
            embed.add_field(name="👥 Followers", value=f"{stats['followers']:,}", inline=True)
            embed.add_field(name="❤️ Likes", value=f"{stats['likes']:,}", inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to fetch TikTok stats. Check logs for details.")
    
    @commands.command(name="update_goals")
    async def update_goals(self, ctx):
        """Updates goals based on TikTok stats"""
        stats = self.fetch_tiktok_stats_web()
        
        if stats:
            for goal in self.goals["Followers"]:
                goal['current'] = min(stats['followers'], goal['total'])
            
            for goal in self.goals["Likes"]:
                goal['current'] = min(stats['likes'], goal['total'])
            
            await ctx.send("✅ Goals updated with latest TikTok stats!")
        else:
            await ctx.send("❌ Failed to update goals. Could not fetch TikTok stats.")
    
async def setup(bot):
    await bot.add_cog(TikTokTracker(bot))
