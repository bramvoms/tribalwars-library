import discord
import os  # Ensure the 'os' module is imported
from discord.ext import commands
from discord.ui import Button, View

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize the bot with the necessary intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary containing scripts and their descriptions
scripts = {
    "aanvallen": {
        "offpack": "Offpack Description: A tool for attacking with full efficiency.",
        "timetool": "TimeTool Description: A tool for calculating attack times."
    },
    "verdedigen": {
        "defpack": "Defpack Description: A defensive tool for creating the best defense.",
        "incs_enhancer": "Incs Enhancer Description: Enhances incoming attack predictions.",
        "snipe_tool": "SnipeTool Description: A tool to assist in sniping units.",
        "tribeshare": "TribeShare Description: A tool for sharing resources within a tribe."
    },
    "kaart": {
        "map_functions": "MapFunctions Description: Helps visualize the game map.",
        "overwatch": "Overwatch Description: A map tracking tool for monitoring the game."
    },
    "farmen": {
        "farmgod": "FarmGod Description: A tool for optimizing farming strategies.",
        "farmshaper": "FarmShaper Description: A tool for shaping farm lists."
    },
    "rooftochten": {
        "massa_rooftochten": "Massa rooftochten Description: A tool for mass raids.",
        "roof_unlocker": "Roof Unlocker Description: A tool for unlocking raid functions."
    },
    "overig": {
        "miscellaneous_tools": "Miscellaneous Tools Description: Various small utility tools."
    }
}

# Main menu buttons (Categories)
class MainMenuButtons(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="Aanvallen", style=discord.ButtonStyle.primary, custom_id="aanvallen"))
        self.add_item(Button(label="Verdedigen", style=discord.ButtonStyle.primary, custom_id="verdedigen"))
        self.add_item(Button(label="Kaart", style=discord.ButtonStyle.primary, custom_id="kaart"))
        self.add_item(Button(label="Farmen", style=discord.ButtonStyle.primary, custom_id="farmen"))
        self.add_item(Button(label="Rooftochten", style=discord.ButtonStyle.primary, custom_id="rooftochten"))
        self.add_item(Button(label="Overig", style=discord.ButtonStyle.primary, custom_id="overig"))

    async def on_button_click(self, interaction: discord.Interaction):
        category = interaction.data["custom_id"]
        if category in scripts:
            # Send the user the subcategory buttons
            await interaction.response.send_message(f"Selected category: {category.capitalize()}", view=SubcategoryButtons(category))
        else:
            await interaction.response.send_message("Invalid category.", ephemeral=True)

# Subcategory buttons (Specific tools within a category)
class SubcategoryButtons(View):
    def __init__(self, category):
        super().__init__()
        self.category = category
        # Add the subcategory buttons dynamically based on the selected category
        subcategories = scripts.get(category, {})
        for subcategory in subcategories:
            self.add_item(Button(label=subcategory.capitalize(), style=discord.ButtonStyle.primary, custom_id=f"{category}_{subcategory}"))
        
        # Add a "Previous" button to go back to the main menu
        self.add_item(Button(label="Previous", style=discord.ButtonStyle.secondary, custom_id="previous"))

    async def on_button_click(self, interaction: discord.Interaction):
        button_id = interaction.data["custom_id"]
        
        # Handle "Previous" button click (go back to the main menu)
        if button_id == "previous":
            await interaction.response.send_message("Returning to the main menu...", view=MainMenuButtons())
        elif "_" in button_id:
            # Extract category and subcategory from the button custom_id
            category, subcategory = button_id.split("_", 1)
            # Check if the subcategory exists in the scripts dictionary
            if subcategory in scripts.get(category, {}):
                await interaction.response.send_message(f"{subcategory.capitalize()} Description: {scripts[category][subcategory]}")
            else:
                await interaction.response.send_message("Subcategory not found.")
        else:
            await interaction.response.send_message("Invalid interaction.", ephemeral=True)

# Slash command to trigger the main menu
@bot.tree.command(name="scripts")
async def scripts_command(interaction: discord.Interaction):
    """Displays the main categories."""
    await interaction.response.send_message("Choose a category:", view=MainMenuButtons())

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Run the bot
if __name__ == '__main__':
    bot.run(os.getenv("DISCORD_TOKEN"))
