import discord
from discord.ext import commands
import os
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

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