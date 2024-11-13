import discord
from discord.ext import commands
import os

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
    for cog in ["scripts_cog", "purge_cog", "am_cog"]:
        await bot.load_extension(f"cogs.{cog}")

# Run the bot and load cogs
if __name__ == "__main__":
    bot.loop.run_until_complete(load_cogs())
    bot.run(os.getenv("DISCORD_TOKEN"))
