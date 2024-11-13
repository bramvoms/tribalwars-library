import discord
from discord.ext import commands
import os
import asyncio
from pathlib import Path

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Initialize the bot with application_id from the environment variable
bot = commands.Bot(
    command_prefix="&",
    intents=intents,
    application_id=int(os.getenv("DISCORD_APPLICATION_ID"))  # Convert to int if required by your hosting environment
)

# Define the bot owner's ID
BOT_OWNER_ID = 284710799321202702  # Replace with your Discord user ID

# Define a global helper function to create an embed
embed_color = discord.Color.from_rgb(221, 205, 165)
thumbnail_url = "https://i.imgur.com/GDJE1uD.png"
footer_icon_url = "https://i.imgur.com/N6Z8wxx.png"  # Same image or different as needed

def create_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=embed_color)
    embed.set_thumbnail(url=thumbnail_url)  # Add the thumbnail image in the top right corner
    embed.add_field(name="\u200b", value="\u200b", inline=False)  # Adds an empty space
    embed.set_footer(icon_url=footer_icon_url, text="TribalWars Library - Created by Victorious")  # Footer with image
    return embed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")

    # Register the context menu command in on_ready
    report_command = app_commands.ContextMenu(
        name="Report to Mods",
        callback=bot.get_cog("ReportToModsCog").report_message
    )
    bot.tree.add_command(report_command)
    
    # Sync and print the registered commands
    try:
        await bot.tree.sync()
        print("Commands synced successfully.")
        print("Registered commands:", bot.tree.get_commands())  # Print the list of commands
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_guild_join(guild):
    # Notify the bot owner via DM when it joins a new guild
    owner = await bot.fetch_user(BOT_OWNER_ID)
    if owner:
        await owner.send(f"The bot has been added to the server: {guild.name} (ID: {guild.id})")
    print(f"Bot joined the server: {guild.name}")

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

@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Commands synced successfully!")
        
# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
