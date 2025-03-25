import discord
from discord.ext import commands
import asyncio
from typing import List, Dict
import random

class TikTokGoal:
    def __init__(self, description: str, target: int, current: int = 0):
        self.description = description
        self.target = target
        self.current = current
    
    def progress_percentage(self) -> float:
        return min((self.current / self.target) * 100, 100)
    
    def progress_bar(self, width: int = 10) -> str:
        filled = int(self.progress_percentage() / 10)
        bar = '█' * filled + '░' * (width - filled)
        return f"{bar} {self.progress_percentage():.1f}%"

class TikTokTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.username = "bunny_desiree"
        self.goals = self._generate_goals()

    def _generate_goals(self) -> List[TikTokGoal]:
        goals = []
        
        # Followers goals
        followers_milestones = [1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000]
        for milestone in followers_milestones:
            goals.append(TikTokGoal(
                f"Reach {milestone:,} followers", 
                milestone, 
                random.randint(int(milestone * 0.5), milestone - 1)
            ))
        
        # Likes goals
        likes_milestones = [10000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000]
        for milestone in likes_milestones:
            goals.append(TikTokGoal(
                f"Accumulate {milestone:,} total likes", 
                milestone, 
                random.randint(int(milestone * 0.5), milestone - 1)
            ))
        
        # Engagement goals
        engagement_goals = [
            TikTokGoal("Average 1% engagement rate", 100000, random.randint(50000, 90000)),
            TikTokGoal("Get 10 viral videos", 10, random.randint(3, 9)),
            TikTokGoal("Maintain 50% follower growth rate", 50, random.randint(20, 45))
        ]
        goals.extend(engagement_goals)
        
        return goals

    async def fetch_tiktok_stats(self):
        """
        Simulate TikTok stats fetching. 
        In a real-world scenario, you'd replace this with an actual API call.
        """
        return {
            "followers": 8452,
            "following": 315,
            "likes": 187654,
            "video_count": 127
        }

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
        embed.add_field(name="📹 Video Count", value=f"{stats['video_count']:,}", inline=True)
        
        # Find and display suggested goal
        suggested_goal = max(
            [goal for goal in self.goals if goal.progress_percentage() < 100], 
            key=lambda x: x.target
        )
        
        # Add suggested goal progress
        embed.add_field(
            name="🎯 Suggested Goal", 
            value=f"**{suggested_goal.description}**\n{suggested_goal.progress_bar()}",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command()
    async def goals(self, ctx):
        # Create pages manually without external menu library
        items_per_page = 10
        total_pages = (len(self.goals) + items_per_page - 1) // items_per_page
        current_page = 0

        while True:
            # Calculate start and end indices for current page
            start = current_page * items_per_page
            end = start + items_per_page
            page_goals = self.goals[start:end]

            # Create embed for current page
            embed = discord.Embed(
                title="🌈 TikTok Goals Dashboard 🌈", 
                color=discord.Color.from_rgb(186, 85, 211)  # Medium Orchid
            )
            
            for goal in page_goals:
                embed.add_field(
                    name=goal.description, 
                    value=f"Progress: {goal.progress_bar()}",
                    inline=False
                )
            
            # Add page navigation
            embed.set_footer(text=f"Page {current_page + 1}/{total_pages}")

            # Send or edit message
            if current_page == 0:
                message = await ctx.send(embed=embed)
                await message.add_reaction('➡️')
                await message.add_reaction('⬅️')
            else:
                await message.edit(embed=embed)

            # Wait for reaction
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['➡️', '⬅️'] and reaction.message.id == message.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                # Remove user's reaction
                await message.remove_reaction(reaction, user)

                # Navigate pages
                if str(reaction.emoji) == '➡️':
                    current_page = min(current_page + 1, total_pages - 1)
                elif str(reaction.emoji) == '⬅️':
                    current_page = max(current_page - 1, 0)

            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

async def setup(bot):
    await bot.add_cog(TikTokTracker(bot))