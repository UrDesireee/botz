import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict
import re

class TikTokGoal:
    def __init__(self, description: str, stat_type: str, milestones: List[int]):
        self.description = description
        self.stat_type = stat_type
        self.milestones = milestones
        self.current_milestone_index = 0

    def update_progress(self, current_value: int):
        # Find the highest milestone reached
        for i, milestone in enumerate(self.milestones):
            if current_value >= milestone:
                self.current_milestone_index = i
            else:
                break

    def get_current_milestone(self):
        return self.milestones[self.current_milestone_index]

    def get_next_milestone(self):
        return self.milestones[min(self.current_milestone_index + 1, len(self.milestones) - 1)]

    def progress_percentage(self, current_value: int) -> float:
        if self.current_milestone_index >= len(self.milestones) - 1:
            return 100.0
        
        current_milestone = self.get_current_milestone()
        next_milestone = self.get_next_milestone()
        
        # Calculate progress between current milestones
        progress = (current_value - current_milestone) / (next_milestone - current_milestone) * 100
        return min(max(progress, 0), 100)

    def progress_bar(self, current_value: int, width: int = 10) -> str:
        percentage = self.progress_percentage(current_value)
        filled = int(percentage / 10)
        bar = '█' * filled + '░' * (width - filled)
        return f"{bar} {percentage:.1f}%"

class TikTokTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.username = "bunny_desiree"
        self.goals = self._generate_goals()
        self.last_stats = None

    def _generate_goals(self) -> List[TikTokGoal]:
        return [
            TikTokGoal(
                "Followers Milestones", 
                "followers", 
                [1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000]
            ),
            TikTokGoal(
                "Likes Milestones", 
                "likes", 
                [10000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000]
            )
        ]

    async def fetch_tiktok_stats(self):
        """
        Fetch TikTok followers and likes using web scraping
        """
        url = f"https://www.tiktok.com/@{self.username}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }) as response:
                    if response.status != 200:
                        return {
                            "followers": 0,
                            "likes": 0
                        }
                    
                    html = await response.text()
                    
                    # Extract followers
                    followers_match = re.search(r'(\d+(?:,\d+)*)\s*Followers', html)
                    followers = int(followers_match.group(1).replace(',', '')) if followers_match else 0
                    
                    # Extract likes
                    likes_match = re.search(r'(\d+(?:,\d+)*)\s*Likes', html)
                    likes = int(likes_match.group(1).replace(',', '')) if likes_match else 0
                    
                    # Update goals
                    for goal in self.goals:
                        if goal.stat_type == "followers":
                            goal.update_progress(followers)
                        elif goal.stat_type == "likes":
                            goal.update_progress(likes)
                    
                    # Cache stats
                    self.last_stats = {
                        "followers": followers,
                        "likes": likes
                    }
                    
                    return self.last_stats
        except Exception as e:
            print(f"Error fetching TikTok stats: {e}")
            return self.last_stats or {"followers": 0, "likes": 0}

    @commands.command()
    async def tiktok(self, ctx):
        # Fetch stats
        stats = await self.fetch_tiktok_stats()
        
        # Create embed
        embed = discord.Embed(
            title=f"🌸 TikTok Stats for @{self.username} 🌸",
            color=discord.Color.from_rgb(255, 105, 180)  # Hot Pink
        )
        
        # Add stats fields
        embed.add_field(name="📊 Followers", value=f"{stats['followers']:,}", inline=True)
        embed.add_field(name="❤️ Total Likes", value=f"{stats['likes']:,}", inline=True)
        
        # Find and display suggested goal
        suggested_goal = max(
            self.goals, 
            key=lambda x: x.get_next_milestone()
        )
        
        # Add suggested goal progress
        embed.add_field(
            name="🎯 Suggested Goal", 
            value=f"**{suggested_goal.description}**\n"
                  f"Next target: {suggested_goal.get_next_milestone():,} {suggested_goal.stat_type}\n"
                  f"{suggested_goal.progress_bar(stats[suggested_goal.stat_type])}",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def goals(self, ctx):
        # Ensure we have the latest stats
        await self.fetch_tiktok_stats()
        
        # Create view with buttons
        class GoalsView(discord.ui.View):
            def __init__(self, cog, ctx):
                super().__init__()
                self.cog = cog
                self.ctx = ctx
                self.current_page = 0

            def create_embed(self):
                goal = self.cog.goals[self.current_page]
                stats = self.cog.last_stats or {"followers": 0, "likes": 0}
                current_value = stats[goal.stat_type]

                embed = discord.Embed(
                    title=f"🌈 {goal.description} 🌈", 
                    color=discord.Color.from_rgb(186, 85, 211)  # Medium Orchid
                )
                
                # Current progress
                embed.add_field(
                    name=f"Current {goal.stat_type.capitalize()}",
                    value=f"{current_value:,}",
                    inline=False
                )
                
                # Milestone tracking
                embed.add_field(
                    name="Milestone Progress",
                    value=goal.progress_bar(current_value),
                    inline=False
                )
                
                # Next milestone details
                next_milestone = goal.get_next_milestone()
                remaining = max(0, next_milestone - current_value)
                embed.add_field(
                    name="Next Milestone",
                    value=f"{next_milestone:,} {goal.stat_type} (Remaining: {remaining:,})",
                    inline=False
                )
                
                return embed

            @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
            async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = (self.current_page - 1) % len(self.cog.goals)
                await interaction.response.edit_message(embed=self.create_embed(), view=self)

            @discord.ui.button(label="Page", style=discord.ButtonStyle.primary, disabled=True)
            async def page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                # This button shows current page and total pages
                pass

            @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.secondary)
            async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = (self.current_page + 1) % len(self.cog.goals)
                await interaction.response.edit_message(embed=self.create_embed(), view=self)

            def update_buttons(self):
                # Update page button
                self.children[1].label = f"Page {self.current_page + 1}/{len(self.cog.goals)}"

        # Create and send the view
        view = GoalsView(self, ctx)
        view.update_buttons()
        
        initial_embed = view.create_embed()
        await ctx.send(embed=initial_embed, view=view)

async def setup(bot):
    await bot.add_cog(TikTokTracker(bot))