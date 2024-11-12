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
scripts = {
    "aanvallen": "Information about attacks: How to organize your troops for an effective attack.",
    "verdedigen": "Information about defense: How to strengthen your village and defend against attacks.",
    "kaart": "Information about the map: How to read the map and use it to your advantage.",
    "farmen": "Information about farming: Tips for gathering resources efficiently.",
    "rooftochten": "Information about raids: How to carry out successful raids on enemy villages.",
    "overig": "Other useful information: Additional strategies and tips that don't fit into other categories."
}

# Create buttons for different categories
class ScriptButtons(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Aanvallen", style=discord.ButtonStyle.primary)
    async def aanvallen_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Respond with Attacks FAQ"""
        await interaction.response.send_message(scripts["aanvallen"])

    @discord.ui.button(label="Verdedigen", style=discord.ButtonStyle.primary)
    async def verdedigen_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Respond with Defending FAQ"""
        await interaction.response.send_message(scripts["verdedigen"])

    @discord.ui.button(label="Kaart", style=discord.ButtonStyle.primary)
    async def kaart_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Respond with Map FAQ"""
        await interaction.response.send_message(scripts["kaart"])

    @discord.ui.button(label="Farmen", style=discord.ButtonStyle.primary)
    async def farmen_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Respond with Farming FAQ"""
        await interaction.response.send_message(scripts["farmen"])

    @discord.ui.button(label="Rooftochten", style=discord.ButtonStyle.primary)
    async def rooftochten_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Respond with Raids FAQ"""
        await interaction.response.send_message(scripts["rooftochten"])

    @discord.ui.button(label="Overig", style=discord.ButtonStyle.primary)
    async def overig_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Respond with Other FAQ"""
        await interaction.response.send_message(scripts["overig"])

# Event for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}({bot.user.id})')

# Slash command for scripts with Buttons
@bot.tree.command(name="scripts")
async def scripts(interaction: discord.Interaction):
    """Shows buttons for different script categories."""
    view = ScriptButtons()  # Create the view with buttons
    await interaction.response.send_message("Choose a category to get more information:", view=view)

# Register the commands when the bot is ready
@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync the slash commands
    print(f'Logged in as {bot.user.name}({bot.user.id})')

# Run the bot using the token stored in environment variables
if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))
