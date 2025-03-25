import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os
import time
import hashlib
import hmac
import base64
import uuid

load_dotenv()

class TikTokTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tiktok_username = "bunny_desiree"
        self.client_key = os.getenv("TIKTOK_CLIENT_KEY")
        self.client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
        
        # Initialize goals dictionary
        self.goals = {
            "Followers": [
                # Beginner Milestones
                {"current": 0, "total": 10, "description": "First 10 Followers"},
                {"current": 0, "total": 25, "description": "Quarter Hundred Followers"},
                {"current": 0, "total": 50, "description": "Half Hundred Followers"},
                {"current": 0, "total": 75, "description": "Three-Quarter Hundred Followers"},
                {"current": 0, "total": 100, "description": "First Hundred Followers"},
                {"current": 0, "total": 250, "description": "Quarter Thousand Followers"},
                {"current": 0, "total": 500, "description": "Half Thousand Followers"},
                {"current": 0, "total": 750, "description": "Three-Quarter Thousand Followers"},
                {"current": 0, "total": 1000, "description": "First Thousand Followers"},
                
                # Growing Milestones
                {"current": 0, "total": 1500, "description": "Fifteen Hundred Followers"},
                {"current": 0, "total": 2000, "description": "Two Thousand Followers"},
                {"current": 0, "total": 2500, "description": "Twenty-Five Hundred Followers"},
                {"current": 0, "total": 3000, "description": "Three Thousand Followers"},
                {"current": 0, "total": 4000, "description": "Four Thousand Followers"},
                {"current": 0, "total": 5000, "description": "Five Thousand Followers"},
                
                # Mid-Tier Milestones
                {"current": 0, "total": 7500, "description": "Seven-Half Thousand Followers"},
                {"current": 0, "total": 10000, "description": "Ten Thousand Followers"},
                {"current": 0, "total": 15000, "description": "Fifteen Thousand Followers"},
                {"current": 0, "total": 20000, "description": "Twenty Thousand Followers"},
                {"current": 0, "total": 25000, "description": "Twenty-Five Thousand Followers"},
                {"current": 0, "total": 30000, "description": "Thirty Thousand Followers"},
                
                # Advanced Milestones
                {"current": 0, "total": 40000, "description": "Forty Thousand Followers"},
                {"current": 0, "total": 50000, "description": "Fifty Thousand Followers"},
                {"current": 0, "total": 60000, "description": "Sixty Thousand Followers"},
                {"current": 0, "total": 75000, "description": "Seventy-Five Thousand Followers"},
                {"current": 0, "total": 100000, "description": "Hundred Thousand Followers"},
                
                # Elite Milestones
                {"current": 0, "total": 150000, "description": "Hundred Fifty Thousand Followers"},
                {"current": 0, "total": 200000, "description": "Two Hundred Thousand Followers"},
                {"current": 0, "total": 250000, "description": "Quarter Million Followers"},
                {"current": 0, "total": 300000, "description": "Three Hundred Thousand Followers"},
                {"current": 0, "total": 500000, "description": "Half Million Followers"},
                {"current": 0, "total": 750000, "description": "Three-Quarter Million Followers"},
                {"current": 0, "total": 1000000, "description": "One Million Followers"},
                
                # Legendary Milestones
                {"current": 0, "total": 1500000, "description": "One-Half Million Followers"},
                {"current": 0, "total": 2000000, "description": "Two Million Followers"},
                {"current": 0, "total": 3000000, "description": "Three Million Followers"},
                {"current": 0, "total": 5000000, "description": "Five Million Followers"}
            ],
            "Likes": [
                # Beginner Likes
                {"current": 0, "total": 10, "description": "First 10 Likes"},
                {"current": 0, "total": 25, "description": "Quarter Hundred Likes"},
                {"current": 0, "total": 50, "description": "Half Hundred Likes"},
                {"current": 0, "total": 75, "description": "Three-Quarter Hundred Likes"},
                {"current": 0, "total": 100, "description": "First Hundred Likes"},
                {"current": 0, "total": 250, "description": "Quarter Thousand Likes"},
                {"current": 0, "total": 500, "description": "Half Thousand Likes"},
                {"current": 0, "total": 750, "description": "Three-Quarter Thousand Likes"},
                {"current": 0, "total": 1000, "description": "First Thousand Likes"},
                
                # Growing Likes
                {"current": 0, "total": 2500, "description": "Twenty-Five Hundred Likes"},
                {"current": 0, "total": 5000, "description": "Five Thousand Likes"},
                {"current": 0, "total": 7500, "description": "Seven-Half Thousand Likes"},
                {"current": 0, "total": 10000, "description": "Ten Thousand Likes"},
                {"current": 0, "total": 25000, "description": "Twenty-Five Thousand Likes"},
                {"current": 0, "total": 50000, "description": "Fifty Thousand Likes"},
                
                # Mid-Tier Likes
                {"current": 0, "total": 75000, "description": "Seventy-Five Thousand Likes"},
                {"current": 0, "total": 100000, "description": "Hundred Thousand Likes"},
                {"current": 0, "total": 250000, "description": "Quarter Million Likes"},
                {"current": 0, "total": 500000, "description": "Half Million Likes"},
                {"current": 0, "total": 750000, "description": "Three-Quarter Million Likes"},
                {"current": 0, "total": 1000000, "description": "One Million Likes"},
                
                # Advanced Likes
                {"current": 0, "total": 2500000, "description": "Two-Half Million Likes"},
                {"current": 0, "total": 5000000, "description": "Five Million Likes"},
                {"current": 0, "total": 10000000, "description": "Ten Million Likes"},
                {"current": 0, "total": 25000000, "description": "Twenty-Five Million Likes"},
                {"current": 0, "total": 50000000, "description": "Fifty Million Likes"},
                {"current": 0, "total": 100000000, "description": "Hundred Million Likes"}
            ],
            "Views": [
                # Beginner Views
                {"current": 0, "total": 10, "description": "First 10 Views"},
                {"current": 0, "total": 25, "description": "Quarter Hundred Views"},
                {"current": 0, "total": 50, "description": "Half Hundred Views"},
                {"current": 0, "total": 75, "description": "Three-Quarter Hundred Views"},
                {"current": 0, "total": 100, "description": "First Hundred Views"},
                {"current": 0, "total": 250, "description": "Quarter Thousand Views"},
                {"current": 0, "total": 500, "description": "Half Thousand Views"},
                {"current": 0, "total": 750, "description": "Three-Quarter Thousand Views"},
                {"current": 0, "total": 1000, "description": "First Thousand Views"},
                
                # Growing Views
                {"current": 0, "total": 2500, "description": "Twenty-Five Hundred Views"},
                {"current": 0, "total": 5000, "description": "Five Thousand Views"},
                {"current": 0, "total": 7500, "description": "Seven-Half Thousand Views"},
                {"current": 0, "total": 10000, "description": "Ten Thousand Views"},
                {"current": 0, "total": 25000, "description": "Twenty-Five Thousand Views"},
                {"current": 0, "total": 50000, "description": "Fifty Thousand Views"},
                
                # Mid-Tier Views
                {"current": 0, "total": 75000, "description": "Seventy-Five Thousand Views"},
                {"current": 0, "total": 100000, "description": "Hundred Thousand Views"},
                {"current": 0, "total": 250000, "description": "Quarter Million Views"},
                {"current": 0, "total": 500000, "description": "Half Million Views"},
                {"current": 0, "total": 750000, "description": "Three-Quarter Million Views"},
                {"current": 0, "total": 1000000, "description": "One Million Views"},
                
                # Advanced Views
                {"current": 0, "total": 2500000, "description": "Two-Half Million Views"},
                {"current": 0, "total": 5000000, "description": "Five Million Views"},
                {"current": 0, "total": 10000000, "description": "Ten Million Views"},
                {"current": 0, "total": 25000000, "description": "Twenty-Five Million Views"},
                {"current": 0, "total": 50000000, "description": "Fifty Million Views"},
                {"current": 0, "total": 100000000, "description": "Hundred Million Views"},
                {"current": 0, "total": 250000000, "description": "Quarter Billion Views"},
                {"current": 0, "total": 500000000, "description": "Half Billion Views"},
                {"current": 0, "total": 1000000000, "description": "One Billion Views"}
            ]
        }
        
    def generate_auth_params(self):
        """Generate authorization parameters for TikTok API"""
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4())
        
        # Base parameters
        params = {
            'client_key': self.client_key,
            'timestamp': timestamp,
            'nonce': nonce
        }
        
        # Sort parameters alphabetically
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        
        # Create signature string
        signature_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # Create HMAC-SHA256 signature
        signature = hmac.new(
            self.client_secret.encode('utf-8'), 
            signature_string.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        # Add signature to params
        params['sign'] = signature
        
        return params
    
    def get_access_token(self):
        """Obtain access token from TikTok OAuth"""
        token_url = "https://open.tiktokapis.com/v2/oauth/token/"
        
        # Prepare token request parameters
        data = {
            'client_key': self.client_key,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            # Use data= instead of json=
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token')
            else:
                print(f"Token Error: {response.status_code} - {response.text}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"Network Error obtaining access token: {e}")
            return None
        except ValueError as e:
            print(f"JSON Parsing Error: {e}")
            return None
    
    def fetch_tiktok_stats_api(self):
        """Fetch TikTok stats using the official TikTok Open API"""
        # First, get access token
        access_token = self.get_access_token()
        if not access_token:
            print("Failed to obtain access token")
            return None
        
        # Endpoint for user info
        url = "https://open.tiktokapis.com/v2/user/info/"
        
        # Generate authentication parameters
        auth_params = self.generate_auth_params()
        
        # Headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Request body
        body = {
            "fields": ["follower_count", "likes_count", "video_count"],
            "username": self.tiktok_username
        }
        
        try:
            response = requests.post(url, json=body, headers=headers, params=auth_params)
            
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                
                # Extract user statistics
                user_data = data.get('data', {}).get('user', {})
                return {
                    "followers": user_data.get('follower_count', 0),
                    "likes": user_data.get('likes_count', 0),
                    "views": user_data.get('video_count', 0)  # Note: this might not be total views
                }
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"Network Error fetching TikTok stats: {e}")
            return None
        except ValueError as e:
            print(f"JSON Parsing Error: {e}")
            return None
    
    @commands.command(name="tiktok")
    async def tiktok_stats(self, ctx):
        """Command to display TikTok stats with enhanced error handling"""
        await ctx.trigger_typing()
    
        # Check API credentials first
        if not self.client_key or not self.client_secret:
            await ctx.send("❌ TikTok API credentials are missing!")
            return
    
        # Try to get access token
        access_token = self.get_access_token()
        if not access_token:
            await ctx.send("❌ Failed to obtain TikTok API access token!")
            return
    
        # Fetch stats
        stats = self.fetch_tiktok_stats_api()
    
        if stats:
            embed = discord.Embed(
                title=f"🔴 TikTok Stats for @{self.tiktok_username}",
                color=discord.Color.red()
            )
            embed.add_field(name="👥 Followers", value=f"{stats['followers']:,}", inline=True)
            embed.add_field(name="❤️ Likes", value=f"{stats['likes']:,}", inline=True)
            embed.add_field(name="📹 Video Count", value=f"{stats['views']:,}", inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to fetch TikTok stats. Check API configuration and credentials.")
    
    def create_goals_embed(self, page=0):
        """Creates paginated embed for goals"""
        # Flatten goals into a single list
        goals = (
            self.goals["Followers"] + 
            self.goals["Likes"] + 
            self.goals["Views"]
        )
        
        items_per_page = 10
        total_pages = (len(goals) - 1) // items_per_page + 1
        start_index = page * items_per_page
        goals_to_show = goals[start_index:start_index + items_per_page]
        
        embed = discord.Embed(
            title="🏆 TikTok Goals",
            description=f"Page {page + 1}/{total_pages}",
            color=discord.Color.gold()
        )
        
        for goal in goals_to_show:
            progress = (goal['current'] / goal['total']) * 100
            embed.add_field(
                name=f"🎯 {goal['description']}",
                value=f"Progress: {progress:.2f}% ({goal['current']} / {goal['total']})",
                inline=False
            )
        
        return embed, total_pages

    @commands.command(name="goals")
    async def show_goals(self, ctx, page: int = 0):
        """Command to display paginated goals"""
        embed, total_pages = self.create_goals_embed(page)
        
        async def prev_callback(interaction: discord.Interaction):
            nonlocal page
            if page > 0:
                page -= 1
                new_embed, _ = self.create_goals_embed(page)
                await interaction.response.edit_message(embed=new_embed, view=create_buttons())
        
        async def next_callback(interaction: discord.Interaction):
            nonlocal page
            if page < total_pages - 1:
                page += 1
                new_embed, _ = self.create_goals_embed(page)
                await interaction.response.edit_message(embed=new_embed, view=create_buttons())
        
        def create_buttons():
            new_view = discord.ui.View()
            prev_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.gray, disabled=(page == 0))
            prev_button.callback = prev_callback
            new_view.add_item(prev_button)
            
            page_button = discord.ui.Button(label=f"Page {page + 1}/{total_pages}", style=discord.ButtonStyle.blurple, disabled=True)
            new_view.add_item(page_button)
            
            next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.gray, disabled=(page == total_pages - 1))
            next_button.callback = next_callback
            new_view.add_item(next_button)
            
            return new_view
        
        await ctx.send(embed=embed, view=create_buttons())

    @commands.command(name="test_tiktok_token")
    async def test_tiktok_token(self, ctx):
        """Manually test TikTok API token generation"""
        token = self.get_access_token()
    
        if token:
            await ctx.send(f"Token successfully generated! First 10 chars: {token[:10]}...")
        else:
            await ctx.send("Failed to generate token. Check console for details.")

    @commands.command(name="update_goals")
    async def update_goals(self, ctx):
        """Update goals based on current TikTok stats"""
        stats = self.fetch_tiktok_stats_api()
        
        if stats:
            # Update goals for Followers
            for goal in self.goals["Followers"]:
                goal['current'] = min(stats['followers'], goal['total'])
            
            # Update goals for Likes
            for goal in self.goals["Likes"]:
                goal['current'] = min(stats['likes'], goal['total'])
            
            # Update goals for Views
            for goal in self.goals["Views"]:
                goal['current'] = min(stats['views'], goal['total'])
            
            await ctx.send("Goals have been updated based on current TikTok stats!")
        else:
            await ctx.send("Failed to update goals. Could not fetch TikTok stats.")

async def setup(bot):
    await bot.add_cog(TikTokTracker(bot))