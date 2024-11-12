import discord
import os
from discord.ext import commands
from discord import ui

# Set up intents (as before)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Define the main scripts and their subcategories
scripts = {
    "aanvallen": {
        "offpack": "Offpack Description",
        "timetool": "TimeTool Description"
    },
    "verdedigen": {
        "defpack": "Defpack Description",
        "incs_enhancer": "Incs Enhancer Description",
        "snipe_tool": "SnipeTool Description",
        "tribeshare": "TribeShare Description"
    },
    "kaart": {
        "map_functions": "MapFunctions Description",
        "overwatch": "Overwatch Description"
    },
    "farmen": {
        "farmgod": "FarmGod Description",
        "farmshaper": "FarmShaper Description"
    },
    "rooftochten": {
        "massa_rooftochten": "Massa rooftochten Description",
        "roof_unlocker": "Roof unlocker Description"
    },
    "overig": {
        "miscellaneous_tools": "Miscellaneous Tools Description"
    }
}

# Create subcategory buttons
class SubcategoryButtons(ui.View):
    def __init__(self, script_name):
        super().__init__()
        self.script_name = script_name

        # Create the subcategory buttons dynamically based on the selected script category
        subcategories = scripts.get(script_name, {})

        if subcategories:
            for subcategory in subcategories:
                # Ensure each button has a unique custom_id based on the subcategory
                self.add_item(ui.Button(label=subcategory.capitalize(), style=discord.ButtonStyle.primary, custom_id=f"{script_name}_{subcategory}"))
        
        # Add a "previous" button to go back to the main script categories
        self.add_item(ui.Button(label="Previous", style=discord.ButtonStyle.secondary, custom_id="previous"))

    async def on_button_click(self, interaction: discord.Interaction):
        button_id = interaction.data["custom_id"]

        # If "Previous" is clicked, go back to the main categories
        if button_id == "previous":
            await interaction.response.send_message("Returning to the main menu...", view=MainMenuButtons())
        # Handle the subcategory button interaction
        elif "_" in button_id:
            # Split the custom_id into script_name and subcategory
            script_name, subcategory = button_id.split("_", 1)
            if subcategory in scripts.get(script_name, {}):
                await interaction.response.send_message(f"You selected {subcategory.capitalize()}: {scripts[script_name][subcategory]}")
            else:
                await interaction.response.send_message("Subcategory not found.")
        else:
            await interaction.response.send_message("Invalid button interaction.")

class MainMenuButtons(ui.View):
    def __init__(self):
        super().__init__()

        # Add the main category buttons
        self.add_item(ui.Button(label="Aanvallen", style=discord.ButtonStyle.primary, custom_id="aanvallen"))
        self.add_item(ui.Button(label="Verdedigen", style=discord.ButtonStyle.primary, custom_id="verdedigen"))
        self.add_item(ui.Button(label="Kaart", style=discord.ButtonStyle.primary, custom_id="kaart"))
        self.add_item(ui.Button(label="Farmen", style=discord.ButtonStyle.primary, custom_id="farmen"))
        self.add_item(ui.Button(label="Rooftochten", style=discord.ButtonStyle.primary, custom_id="rooftochten"))
        self.add_item(ui.Button(label="Overig", style=discord.ButtonStyle.primary, custom_id="overig"))

    # Handle interaction for category selection
    async def on_button_click(self, interaction: discord.Interaction):
        category = interaction.data["custom_id"]

        if category in scripts:
            # Send back the subcategories when a category is selected
            await interaction.response.send_message(f"You selected {category.capitalize()}!", view=SubcategoryButtons(category))
        else:
            await interaction.response.send_message("No valid category selected.")

# Command to start the script interaction
@bot.tree.command(name="scripts")
async def scripts_command(interaction: discord.Interaction):
    """Displays the main categories with buttons for each subcategory."""
    await interaction.response.send_message("Choose a category:", view=MainMenuButtons())

# Run the bot
if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))
