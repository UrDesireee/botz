import discord
from discord.ext import commands
import os
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class CogManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load")
    @commands.is_owner()
    async def load_cog(self, ctx, extension: str):
        """Load a cog"""
        try:
            await self.bot.load_extension(f"cogs.{extension}")
            await ctx.send(f"🟢 Cog {extension} loaded successfully!")
        except Exception as e:
            await ctx.send(f"❌ Error loading cog {extension}: {str(e)}")

    @commands.command(name="unload")
    @commands.is_owner()
    async def unload_cog(self, ctx, extension: str):
        """Unload a cog"""
        try:
            await self.bot.unload_extension(f"cogs.{extension}")
            await ctx.send(f"🔴 Cog {extension} unloaded successfully!")
        except Exception as e:
            await ctx.send(f"❌ Error unloading cog {extension}: {str(e)}")

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload_cog(self, ctx, extension: str):
        """Reload a cog"""
        try:
            await self.bot.reload_extension(f"cogs.{extension}")
            await ctx.send(f"🔄 Cog {extension} reloaded successfully!")
        except Exception as e:
            await ctx.send(f"❌ Error reloading cog {extension}: {str(e)}")

    @commands.command(name="list_cogs")
    @commands.is_owner()
    async def list_cogs(self, ctx):
        """List all available cogs"""
        try:
            # Assumes cogs are in a 'cogs' directory
            cog_files = [f[:-3] for f in os.listdir('cogs') if f.endswith('.py')]
            
            # Separate loaded and unloaded cogs
            loaded_cogs = [cog for cog in self.bot.extensions.keys()]
            loaded_cog_names = [cog.split('.')[-1] for cog in loaded_cogs]
            
            unloaded_cogs = [cog for cog in cog_files if cog not in loaded_cog_names]
            
            embed = discord.Embed(title="🤖 Cog Management", color=discord.Color.blue())
            
            # Add loaded cogs
            embed.add_field(
                name="✅ Loaded Cogs", 
                value="\n".join(loaded_cog_names) if loaded_cog_names else "No cogs loaded", 
                inline=False
            )
            
            # Add unloaded cogs
            embed.add_field(
                name="❌ Unloaded Cogs", 
                value="\n".join(unloaded_cogs) if unloaded_cogs else "All cogs loaded", 
                inline=False
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error listing cogs: {str(e)}")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    print('------')

# Load cogs function
async def load_extensions():
    # Create cogs directory if it doesn't exist
    if not os.path.exists('./cogs'):
        os.makedirs('./cogs')
    
    # Add CogManager to bot
    await bot.add_cog(CogManager(bot))
    
    # Load all cogs
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded extension: {filename[:-3]}')
            except Exception as e:
                print(f'Failed to load extension {filename[:-3]}')
                print(f'Error: {e}')

# Run the bot
async def main():
    # Load environment variables
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        print("Error: DISCORD_TOKEN environment variable not set")
        return
    
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

# Entry point
if __name__ == "__main__":
    asyncio.run(main())