import discord
from discord.ext import commands
import os
import asyncio
from pathlib import Path

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Define a global helper function to create an embed
embed_color = discord.Color.from_rgb(255, 255, 0)

def create_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=embed_color)
    embed.set_footer(text="Created by Victorious")
    return embed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()  # Sync app commands with Discord

async def load_cogs():
    # Path to the `cogs` directory
    cogs_path = Path("cogs")
    
    # Iterate over all `.py` files in the `cogs` directory
    for cog_file in cogs_path.glob("*.py"):
        # Load each cog by constructing its Python module path
        cog_name = f"cogs.{cog_file.stem}"  # `stem` gives the filename without the extension
        await bot.load_extension(cog_name)
        print(f"Loaded cog: {cog_name}")

async def main():
    await load_cogs()  # Load all cogs asynchronously
    await bot.start(os.getenv("DISCORD_TOKEN"))  # Start the bot

# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
