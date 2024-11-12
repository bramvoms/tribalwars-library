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

# Create buttons for different categories
class FAQButtons(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Help", style=discord.ButtonStyle.primary)
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Respond with help FAQ"""
        await interaction.response.send_message(faqs["help"])

    @discord.ui.button(label="Rules", style=discord.ButtonStyle.primary)
    async def rules_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Respond with rules FAQ"""
        await interaction.response.send_message(faqs["rules"])

    @discord.ui.button(label="Commands", style=discord.ButtonStyle.primary)
    async def commands_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Respond with commands FAQ"""
        await interaction.response.send_message(faqs["commands"])

# Event for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}({bot.user.id})')

# Slash command for ping
@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

# Slash command for FAQ with Buttons
@bot.tree.command(name="faq")
async def faq(interaction: discord.Interaction):
    """Shows buttons for different FAQ categories."""
    view = FAQButtons()  # Create the view with buttons
    await interaction.response.send_message("Choose a category to get more information:", view=view)

# Register the commands when the bot is ready
@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync the slash commands
    print(f'Logged in as {bot.user.name}({bot.user.id})')

# Run the bot using the token stored in environment variables
if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))
