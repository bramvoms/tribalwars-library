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
    try:
        await bot.tree.sync()  # Syncs commands with Discord
        print("Commands synced successfully.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

async def load_cogs():
    # Define the cogs_path based on the location of main.py
    base_dir = Path(__file__).parent
    cogs_path = base_dir / "cogs"
    
    print(f"Loading cogs from: {cogs_path.resolve()}")  # Log the absolute path

    if not cogs_path.exists() or not cogs_path.is_dir():
        print("Error: Cogs directory does not exist or is not a directory.")
        return

    # Iterate over all `.py` files in the `cogs` directory
    for cog_file in cogs_path.glob("*.py"):
        print(f"Found cog file: {cog_file.name}")
        cog_name = f"cogs.{cog_file.stem}"  # `stem` gives the filename without the extension

        try:
            await bot.load_extension(cog_name)
            print(f"Successfully loaded cog: {cog_name}")
        except Exception as e:
            print(f"Failed to load cog {cog_name}: {e}")
            
async def main():
    await load_cogs()  # Load all cogs asynchronously
    await bot.start(os.getenv("DISCORD_TOKEN"))  # Start the bot
    
@bot.command(name="reload", help="Reloads a specified cog.")
@commands.is_owner()  # Only the bot owner can use this command
async def reload(ctx, cog: str):
    try:
        await bot.unload_extension(f"cogs.{cog}")
        await bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"Successfully reloaded `{cog}`.")
    except Exception as e:
        await ctx.send(f"Failed to reload `{cog}`: {e}")    
        
# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
