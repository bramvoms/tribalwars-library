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
    "aanvallen": "Offpack, TimeTool",
    "verdedigen": "Defpack, Incs Enhancer, SnipeTool, TribeShare",
    "kaart": "MapFunctions, Overwatch",
    "farmen": "FarmGod, FarmShaper",
    "rooftochten": "Massa rooftochten, Roof unlocker",
    "overig": "Miscellaneous Tools"
}

# Create subcategory buttons
class SubcategoryButtons(ui.View):
    def __init__(self, script_name):
        super().__init__()
        self.script_name = script_name

        # Create the buttons for subcategories
        if self.script_name == "aanvallen":
            self.add_item(ui.Button(label="Offpack", style=discord.ButtonStyle.primary, custom_id="offpack"))
            self.add_item(ui.Button(label="TimeTool", style=discord.ButtonStyle.primary, custom_id="timetool"))
        elif self.script_name == "verdedigen":
            self.add_item(ui.Button(label="Defpack", style=discord.ButtonStyle.primary, custom_id="defpack"))
            self.add_item(ui.Button(label="Incs Enhancer", style=discord.ButtonStyle.primary, custom_id="incs_enhancer"))
            self.add_item(ui.Button(label="SnipeTool", style=discord.ButtonStyle.primary, custom_id="snipe_tool"))
            self.add_item(ui.Button(label="TribeShare", style=discord.ButtonStyle.primary, custom_id="tribeshare"))
        elif self.script_name == "kaart":
            self.add_item(ui.Button(label="MapFunctions", style=discord.ButtonStyle.primary, custom_id="map_functions"))
            self.add_item(ui.Button(label="Overwatch", style=discord.ButtonStyle.primary, custom_id="overwatch"))
        elif self.script_name == "farmen":
            self.add_item(ui.Button(label="FarmGod", style=discord.ButtonStyle.primary, custom_id="farmgod"))
            self.add_item(ui.Button(label="FarmShaper", style=discord.ButtonStyle.primary, custom_id="farmshaper"))
        elif self.script_name == "rooftochten":
            self.add_item(ui.Button(label="Massa rooftochten", style=discord.ButtonStyle.primary, custom_id="massa_rooftochten"))
            self.add_item(ui.Button(label="Roof unlocker", style=discord.ButtonStyle.primary, custom_id="roof_unlocker"))
        else:
            self.add_item(ui.Button(label="No subcategories", style=discord.ButtonStyle.primary, custom_id="none"))

    # Button interaction callback functions
    async def on_button_click(self, interaction: discord.Interaction):
        button_id = interaction.data["custom_id"]
        
        # Subcategory response handling based on button pressed
        if button_id == "offpack":
            await interaction.response.send_message("You pressed Offpack!")
        elif button_id == "timetool":
            await interaction.response.send_message("You pressed TimeTool!")
        elif button_id == "defpack":
            await interaction.response.send_message("You pressed Defpack!")
        elif button_id == "incs_enhancer":
            await interaction.response.send_message("You pressed Incs Enhancer!")
        elif button_id == "snipe_tool":
            await interaction.response.send_message("You pressed SnipeTool!")
        elif button_id == "tribeshare":
            await interaction.response.send_message("You pressed TribeShare!")
        elif button_id == "map_functions":
            await interaction.response.send_message("You pressed MapFunctions!")
        elif button_id == "overwatch":
            await interaction.response.send_message("You pressed Overwatch!")
        elif button_id == "farmgod":
            await interaction.response.send_message("You pressed FarmGod!")
        elif button_id == "farmshaper":
            await interaction.response.send_message("You pressed FarmShaper!")
        elif button_id == "massa_rooftochten":
            await interaction.response.send_message("You pressed Massa rooftochten!")
        elif button_id == "roof_unlocker":
            await interaction.response.send_message("You pressed Roof unlocker!")
        else:
            await interaction.response.send_message("No valid subcategory button pressed.")

# Main command for scripts
@bot.tree.command(name="scripts")
async def scripts_command(interaction: discord.Interaction):
    """Displays the main categories with buttons for each subcategory."""
    buttons = ui.View()  # Create a new view to hold buttons
    
    # Add main category buttons
    buttons.add_item(ui.Button(label="Aanvallen", style=discord.ButtonStyle.primary, custom_id="aanvallen"))
    buttons.add_item(ui.Button(label="Verdedigen", style=discord.ButtonStyle.primary, custom_id="verdedigen"))
    buttons.add_item(ui.Button(label="Kaart", style=discord.ButtonStyle.primary, custom_id="kaart"))
    buttons.add_item(ui.Button(label="Farmen", style=discord.ButtonStyle.primary, custom_id="farmen"))
    buttons.add_item(ui.Button(label="Rooftochten", style=discord.ButtonStyle.primary, custom_id="rooftochten"))
    buttons.add_item(ui.Button(label="Overig", style=discord.ButtonStyle.primary, custom_id="overig"))

    # Send the message with the buttons
    await interaction.response.send_message("Choose a category:", view=buttons)

    # Handle button clicks
    async def button_callback(interaction: discord.Interaction):
        category = interaction.data["custom_id"]
        await interaction.response.send_message(f"You selected: {category}", view=SubcategoryButtons(category))

    for button in buttons.children:
        button.callback = button_callback

# Run the bot
if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))
