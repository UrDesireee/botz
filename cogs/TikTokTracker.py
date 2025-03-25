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
        self.milestones = sorted(milestones)
        self.current_milestone_index = -1
        self.completed_milestones = []

    def update_progress(self, current_value: int) -> List[int]:
        # Track newly achieved milestones
        newly_achieved = []
        
        # Check for new milestones
        for i, milestone in enumerate(self.milestones):
            if current_value >= milestone and milestone not in self.completed_milestones:
                self.current_milestone_index = i
                self.completed_milestones.append(milestone)
                newly_achieved.append(milestone)
        
        return newly_achieved

    def get_current_milestone(self):
        return self.milestones[self.current_milestone_index] if self.current_milestone_index >= 0 else 0

    def get_next_milestone(self):
        if self.current_milestone_index >= len(self.milestones) - 1:
            return None
        return self.milestones[self.current_milestone_index + 1]

    def progress_percentage(self, current_value: int) -> float:
        # If all milestones are completed
        if self.current_milestone_index >= len(self.milestones) - 1:
            return 100.0
        
        # If no milestones reached yet
        if self.current_milestone_index == -1:
            next_milestone = self.milestones[0]
            return min(current_value / next_milestone * 100, 100)
        
        # Calculate progress between current milestones
        current_milestone = self.get_current_milestone()
        next_milestone = self.get_next_milestone()
        
        if next_milestone is None:
            return 100.0
        
        progress = (current_value - current_milestone) / (next_milestone - current_milestone) * 100
        return min(max(progress, 0), 100)

    def progress_bar(self, current_value: int, width: int = 10) -> str:
        percentage = self.progress_percentage(current_value)
        filled = int(percentage / 10)
        bar = '█' * filled + '░' * (width - filled)
        return f"{bar} {percentage:.1f}%"

    def is_completed(self):
        return self.current_milestone_index >= len(self.milestones) - 1

class TikTokTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.username = "bunny_desiree"
        self.goals = self._generate_goals()
        self.last_stats = None
        self.achievement_channel = None  # Set this to a specific channel for achievements

    def _generate_goals(self) -> List[TikTokGoal]:
        return [
            TikTokGoal(
                "Followers Milestones", 
                "followers", 
                [20, 50, 100, 200, 500, 1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000]
            ),
            TikTokGoal(
                "Likes Milestones", 
                "likes", 
                [10, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000]
            )
        ]

    async def send_achievement_message(self, goal_type: str, milestone: int):
        """Send an achievement message to a specific channel"""
        if not self.achievement_channel:
            # Try to find a general or announcements channel if not set
            self.achievement_channel = discord.utils.get(
                self.bot.get_all_channels(), 
                name=['achievements', 'announcements', 'general']
            )
        
        if self.achievement_channel:
            embed = discord.Embed(
                title="🎉 Goal Achieved! 🎉",
                description=f"**@{self.username}** just reached {milestone:,} {goal_type}!",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="Celebration 🎈", 
                value=f"Congratulations on hitting this amazing milestone! Keep pushing forward to the next goal.",
                inline=False
            )
            
            try:
                await self.achievement_channel.send(embed=embed)
            except Exception as e:
                print(f"Could not send achievement message: {e}")

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
                    
                    # Track achievements
                    for goal in self.goals:
                        newly_achieved = goal.update_progress(
                            followers if goal.stat_type == "followers" else likes
                        )
                        
                        # Send achievement messages
                        for milestone in newly_achieved:
                            await self.send_achievement_message(goal.stat_type, milestone)
                    
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
            [goal for goal in self.goals if not goal.is_completed()], 
            key=lambda x: x.get_next_milestone() or 0
        )
        
        # Add suggested goal progress
        next_milestone = suggested_goal.get_next_milestone()
        current_value = stats[suggested_goal.stat_type]
        
        embed.add_field(
            name="🎯 Suggested Goal", 
            value=f"**{suggested_goal.description}**\n"
                  f"Next target: {next_milestone:,} {suggested_goal.stat_type}\n"
                  f"{suggested_goal.progress_bar(current_value)}",
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
                stats = self.cog.last_stats or {"followers": 0, "likes": 0}
                goal = self.cog.goals[self.current_page]
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
                
                # All milestones with status
                milestone_status = []
                for milestone in goal.milestones:
                    if milestone in goal.completed_milestones:
                        status = "✅ Completed"
                    elif milestone > current_value:
                        status = "🔜 Upcoming"
                    else:
                        status = "🟡 In Progress"
                    
                    milestone_status.append(f"{milestone:,}: {status}")
                
                # Milestone tracking
                embed.add_field(
                    name="Milestone Progress",
                    value="\n".join(milestone_status),
                    inline=False
                )
                
                # Current progress bar
                embed.add_field(
                    name="Overall Progress",
                    value=goal.progress_bar(current_value),
                    inline=False
                )
                
                # Next milestone details
                next_milestone = goal.get_next_milestone()
                if next_milestone:
                    remaining = max(0, next_milestone - current_value)
                    embed.add_field(
                        name="Next Milestone",
                        value=f"{next_milestone:,} {goal.stat_type} (Remaining: {remaining:,})",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="Status",
                        value="🏆 All Milestones Completed!",
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