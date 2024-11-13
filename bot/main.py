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
    cogs_path = Path("cogs")
    for cog_file in cogs_path.glob("*.py"):
        cog_name = f"cogs.{cog_file.stem}"
        try:
            await bot.load_extension(cog_name)
            print(f"Successfully loaded cog: {cog_name}")
        except Exception as e:
            print(f"Failed to load cog {cog_name}: {e}")

async def main():
    await load_cogs()  # Load all cogs asynchronously
    await bot.start(os.getenv("DISCORD_TOKEN"))  # Start the bot
    
@bot.tree.command(name="test", description="A test command to check slash commands.")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("Test command is working!")

# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
