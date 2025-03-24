import discord
from discord.ext import commands
from TikTokApi import TikTokApi
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

class TikTokTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tiktok_username = "bunny_desiree"
        self.goals = {
            "Likes": {
                "current": 0,
                "total": 500000,
                "description": "Reach 500K Total Likes"
            },
            "Followers": {
                "current": 0,
                "total": 50000,
                "description": "Reach 50K Followers"
            },
            "Views": {
                "current": 0,
                "total": 2000000,
                "description": "Reach 2M Total Views"
            }
        }

    async def fetch_tiktok_stats(self):
        """Fetch TikTok account statistics"""
        try:
            async with TikTokApi() as api:
                user = await api.user(username=self.tiktok_username)
                stats = await user.info()
                
                last_video = await user.videos(count=1)
                last_video_stats = last_video[0] if last_video else None

                return {
                    "followers": stats.follower_count,
                    "following": stats.following_count,
                    "total_likes": stats.total_favorited,
                    "total_views": stats.total_view_count,
                    "last_video": {
                        "likes": last_video_stats.stats.digg_count if last_video_stats else 0,
                        "comments": last_video_stats.stats.comment_count if last_video_stats else 0,
                        "shares": last_video_stats.stats.share_count if last_video_stats else 0
                    }
                }
        except Exception as e:
            print(f"Error fetching TikTok stats: {e}")
            return None

    def create_stats_embed(self, stats):
        """Create an embed with TikTok account statistics"""
        embed = discord.Embed(
            title=f"🔴 TikTok Stats for @{self.tiktok_username}",
            color=discord.Color.red()
        )
        
        embed.add_field(name="👥 Followers", value=f"{stats['followers']:,}", inline=True)
        embed.add_field(name="❤️ Total Likes", value=f"{stats['total_likes']:,}", inline=True)
        embed.add_field(name="👀 Total Views", value=f"{stats['total_views']:,}", inline=True)

        if stats['last_video']:
            embed.add_field(name="📹 Last Video Stats", value=(
                f"Likes: {stats['last_video']['likes']:,}\n"
                f"Comments: {stats['last_video']['comments']:,}\n"
                f"Shares: {stats['last_video']['shares']:,}"
            ), inline=False)

        # Update goals
        self.goals['Followers']['current'] = stats['followers']
        self.goals['Likes']['current'] = stats['total_likes']
        self.goals['Views']['current'] = stats['total_views']

        # Add goals progress
        for goal_name, goal_data in self.goals.items():
            progress = min(100, (goal_data['current'] / goal_data['total']) * 100)
            embed.add_field(
                name=f"🎯 {goal_name} Goal",
                value=(
                    f"Progress: {progress:.2f}%\n"
                    f"{goal_data['current']:,} / {goal_data['total']:,}\n"
                    f"{goal_data['description']}"
                ),
                inline=False
            )

        return embed

    @commands.command(name="tiktok")
    async def tiktok_stats(self, ctx):
        """Command to display TikTok account statistics"""
        await ctx.trigger_typing()
        stats = await self.fetch_tiktok_stats()
        
        if stats:
            embed = self.create_stats_embed(stats)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Sorry, could not fetch TikTok statistics.")

    @commands.command(name="goals")
    async def show_goals(self, ctx):
        """Command to display all goals and their progress"""
        embed = discord.Embed(
            title="🏆 TikTok Account Goals",
            description="Tracking progress towards milestones",
            color=discord.Color.gold()
        )

        for goal_name, goal_data in self.goals.items():
            progress = min(100, (goal_data['current'] / goal_data['total']) * 100)
            embed.add_field(
                name=f"🎯 {goal_name} Goal",
                value=(
                    f"Progress: {progress:.2f}%\n"
                    f"{goal_data['current']:,} / {goal_data['total']:,}\n"
                    f"{goal_data['description']}"
                ),
                inline=False
            )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(TikTokTracker(bot))