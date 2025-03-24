import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os

load_dotenv()

class TikTokTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tiktok_username = "bunny_desiree"
        self.api_key = os.getenv("TIKTOK_API_KEY")  # Load API Key from .env

    def fetch_tiktok_stats_api(self):
        """Fetch TikTok stats using an API (preferred method)"""
        url = f"https://api.tiktok.com/user/{self.tiktok_username}"  # Replace with real API URL
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "followers": data.get("follower_count", 0),
                "likes": data.get("total_likes", 0),
                "views": data.get("video_views", 0)
            }
        return None
    
    @commands.command(name="tiktok")
    async def tiktok_stats(self, ctx):
        """Command to display TikTok stats"""
        await ctx.trigger_typing()
        stats = self.fetch_tiktok_stats_api()
        
        if stats:
            embed = discord.Embed(
                title=f"🔴 TikTok Stats for @{self.tiktok_username}",
                color=discord.Color.red()
            )
            embed.add_field(name="👥 Followers", value=f"{stats['followers']:,}", inline=True)
            embed.add_field(name="❤️ Likes", value=f"{stats['likes']:,}", inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to fetch TikTok stats. API might be down.")
    
    def create_goals_embed(self, page=0):
        """Creates paginated embed for goals"""
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

        
        items_per_page = 2
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
        view = discord.ui.View()
        
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

async def setup(bot):
    await bot.add_cog(TikTokTracker(bot))
