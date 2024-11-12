import discord
import os
from discord.ext import commands
from discord import app_commands

# Set up intents (as before)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# FAQ data (you can customize this)
faqs = {
    "help": "I can help answer frequently asked questions! Try using `/faq <topic>`. ",
    "rules": "Please follow the server rules to ensure a friendly environment.",
    "commands": "Available commands are `/faq <topic>`, `/ping`, etc."
}

# Event for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}({bot.user.id})')

# Slash command for ping
@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

# Slash command for FAQ
@bot.tree.command(name="faq")
@app_commands.describe(topic="The topic you want information on")
async def faq(interaction: discord.Interaction, topic: str):
    """Responds with FAQ information based on the topic."""
    if topic.lower() in faqs:
        await interaction.response.send_message(faqs[topic.lower()])
    else:
        await interaction.response.send_message("Sorry, I don’t have information on that topic. Try `/faq help` for more info.")

# Register the commands when the bot is ready
@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync the slash commands
    print(f'Logged in as {bot.user.name}({bot.user.id})')

# Run the bot using the token stored in environment variables
if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))
