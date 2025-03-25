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
        
        # Initialize goals dictionary (removing views, keeping only followers and likes)
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
            ]
        }
    
    def fetch_tiktok_stats_web(self):
        """Fetch TikTok stats using web scraping"""
        try:
            # Send a request to TikTok profile
            url = f"https://www.tiktok.com/@{self.tiktok_username}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            
            # Check if request was successful
            if response.status_code != 200:
                print(f"Failed to fetch page. Status code: {response.status_code}")
                return None
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract followers and likes
            # Note: The exact selectors might change, so this is a hypothetical example
            followers_elem = soup.select_one('strong[title="Followers"]')
            likes_elem = soup.select_one('strong[title="Likes"]')
            
            if not followers_elem or not likes_elem:
                print("Could not find followers or likes elements")
                return None
            
            # Clean and convert stats
            followers = self._clean_number(followers_elem.text)
            likes = self._clean_number(likes_elem.text)
            
            return {
                "followers": followers,
                "likes": likes
            }
        
        except requests.exceptions.RequestException as e:
            print(f"Network Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def _clean_number(self, number_str):
        """Clean and convert number string to integer"""
        # Remove any non-numeric characters except decimal point
        cleaned = ''.join(char for char in number_str if char.isdigit() or char == '.')
        
        # Convert to float first to handle K, M, B suffixes
        try:
            if 'K' in number_str:
                return int(float(cleaned) * 1000)
            elif 'M' in number_str:
                return int(float(cleaned) * 1000000)
            elif 'B' in number_str:
                return int(float(cleaned) * 1000000000)
            return int(float(cleaned))
        except ValueError:
            print(f"Could not convert {number_str} to number")
            return 0
    
    @commands.command(name="tiktok")
    async def tiktok_stats(self, ctx):
        """Command to display TikTok stats with web scraping"""
        await ctx.trigger_typing()
    
        # Fetch stats
        stats = self.fetch_tiktok_stats_web()
    
        if stats:
            embed = discord.Embed(
                title=f"🔴 TikTok Stats for @{self.tiktok_username}",
                color=discord.Color.red()
            )
            embed.add_field(name="👥 Followers", value=f"{stats['followers']:,}", inline=True)
            embed.add_field(name="❤️ Likes", value=f"{stats['likes']:,}", inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to fetch TikTok stats. Check the console for details.")
    
    def create_goals_embed(self, page=0):
        """Creates paginated embed for goals"""
        # Flatten goals into a single list
        goals = (
            self.goals["Followers"] + 
            self.goals["Likes"]
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

    @commands.command(name="update_goals")
    async def update_goals(self, ctx):
        """Update goals based on current TikTok stats"""
        stats = self.fetch_tiktok_stats_web()
        
        if stats:
            # Update goals for Followers
            for goal in self.goals["Followers"]:
                goal['current'] = min(stats['followers'], goal['total'])
            
            # Update goals for Likes
            for goal in self.goals["Likes"]:
                goal['current'] = min(stats['likes'], goal['total'])
            
            await ctx.send("Goals have been updated based on current TikTok stats!")
        else:
            await ctx.send("Failed to update goals. Could not fetch TikTok stats.")

async def setup(bot):
    await bot.add_cog(TikTokTracker(bot))