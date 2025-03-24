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

    async def fetch_tiktok_stats(self):
        """Fetch TikTok account statistics"""
        try:
            async with TikTokApi() as api:
                user = await api.user(username=self.tiktok_username)
                stats = await user.info()
                
                last_video = await user.videos(count=1)
                last_video_stats = last_video[0] if last_video else None

                # Update goals
                for category in ['Followers', 'Likes', 'Views']:
                    for goal in self.goals[category]:
                        if category == 'Followers':
                            goal['current'] = stats.follower_count
                        elif category == 'Likes':
                            goal['current'] = stats.total_favorited
                        elif category == 'Views':
                            goal['current'] = stats.total_view_count

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

        # Add progress for top 5 closest goals for each category
        categories = ['Followers', 'Likes', 'Views']
        for category in categories:
            # Sort goals and find closest goals
            sorted_goals = sorted(
                self.goals[category], 
                key=lambda x: abs(x['total'] - stats[f'total_{category.lower()}'])
            )
            
            # Take top 5 closest goals
            top_goals = sorted_goals[:5]
            
            category_embed_text = ""
            for goal in top_goals:
                progress = min(100, (stats[f'total_{category.lower()}'] / goal['total']) * 100)
                category_embed_text += (
                    f"🎯 {goal['description']}: "
                    f"{progress:.2f}% ({stats[f'total_{category.lower()}']:,}/{goal['total']:,})\n"
                )
            
            embed.add_field(
                name=f"🏆 Top {category} Goals",
                value=category_embed_text,
                inline=False
            )

        return embed

    @commands.command(name="tiktok")
    async def tiktok_stats(self, ctx):
        """Command to display TikTok account statistics"""
        await ctx.trigger_typing()
        try:
            stats = await self.fetch_tiktok_stats()
            
            if stats:
                embed = self.create_stats_embed(stats)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Sorry, could not fetch TikTok statistics.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    def create_goals_embed(self, page=0, category=None):
        """Create an embed showing goals with pagination"""
        if category:
            # Filter goals for specific category
            category_goals = self.goals.get(category, [])
            goals_to_show = category_goals[page*10:(page+1)*10]
        else:
            # Default to showing all categories
            all_goals = []
            for cat_goals in self.goals.values():
                all_goals.extend(cat_goals)
            goals_to_show = all_goals[page*10:(page+1)*10]

        embed = discord.Embed(
            title="🏆 Comprehensive TikTok Goals",
            description="Tracking progress across multiple milestones",
            color=discord.Color.gold()
        )

        for goal in goals_to_show:
            progress = min(100, (goal['current'] / goal['total']) * 100)
            embed.add_field(
                name=f"🎯 {goal['description']}",
                value=(
                    f"Progress: {progress:.2f}%\n"
                    f"{goal['current']:,} / {goal['total']:,}"
                ),
                inline=False
            )

        return embed

    @commands.command(name="goals")
    async def show_goals(self, ctx, category=None, page: int = 0):
        """Command to display goals with optional category and pagination"""
        try:
            embed = self.create_goals_embed(page, category)
            
            # Create a view with buttons
            view = discord.ui.View()
            
            async def prev_callback(interaction: discord.Interaction):
                new_page = max(0, page - 1)
                new_embed = self.create_goals_embed(new_page, category)
                await interaction.response.edit_message(embed=new_embed)

            async def next_callback(interaction: discord.Interaction):
                new_page = page + 1
                new_embed = self.create_goals_embed(new_page, category)
                await interaction.response.edit_message(embed=new_embed)

            prev_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.gray)
            prev_button.callback = prev_callback
            view.add_item(prev_button)

            next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.gray)
            next_button.callback = next_callback
            view.add_item(next_button)

            await ctx.send(embed=embed, view=view)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(TikTokTracker(bot))