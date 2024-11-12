import discord
import os
from discord.ext import commands
from discord import app_commands

# Set up intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# FAQ data for each subcategory
faq_data = {
    "aanvallen": {
        "offpack": "Offpack: A strategy tool to organize your offensive packs efficiently.",
        "timetool": "TimeTool: Helps you calculate the best times to send troops for maximum efficiency."
    },
    "verdedigen": {
        "defpack": "Defpack: A defensive pack setup to help protect your village.",
        "incs_enhancer": "Incs Enhancer: A tool for better managing incoming attacks and defenses.",
        "snipe_tool": "SnipeTool: Tool to snipe enemy troops and minimize your losses.",
        "tribe_share": "TribeShare: Share resources or troops within your tribe for better support."
    },
    "kaart": {
        "mapfunctions": "MapFunctions: Allows you to enhance the map for better strategic planning.",
        "overwatch": "Overwatch: A system to monitor enemy movements and predict attacks."
    },
    "farmen": {
        "farmgod": "FarmGod: Automates farming for resources across multiple villages.",
        "farmshaper": "FarmShaper: A tool to organize farming routes and optimize resource collection."
    },
    "rooftochten": {
        "massa_rooftochten": "Massa Rooftochten: Automates mass raids to plunder resources.",
        "roof_unlocker": "Roof Unlocker: Helps unlock specific targets for your raids."
    },
    "overig": "Other useful tools that don't fit into any category."
}

# Create buttons for different categories
class ScriptButtons(discord.ui.View):
    def __init__(self):
        super().__init__()

    # Category Buttons
    @discord.ui.button(label="Aanvallen", style=discord.ButtonStyle.primary)
    async def aanvallen_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shows subcategory buttons for Aanvallen"""
        view = SubcategoryButtons("aanvallen")  # Subcategories for Aanvallen
        await interaction.response.send_message("Choose a subcategory for Aanvallen:", view=view)

    @discord.ui.button(label="Verdedigen", style=discord.ButtonStyle.primary)
    async def verdedigen_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shows subcategory buttons for Verdedigen"""
        view = SubcategoryButtons("verdedigen")  # Subcategories for Verdedigen
        await interaction.response.send_message("Choose a subcategory for Verdedigen:", view=view)

    @discord.ui.button(label="Kaart", style=discord.ButtonStyle.primary)
    async def kaart_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shows subcategory buttons for Kaart"""
        view = SubcategoryButtons("kaart")  # Subcategories for Kaart
        await interaction.response.send_message("Choose a subcategory for Kaart:", view=view)

    @discord.ui.button(label="Farmen", style=discord.ButtonStyle.primary)
    async def farmen_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shows subcategory buttons for Farmen"""
        view = SubcategoryButtons("farmen")  # Subcategories for Farmen
        await interaction.response.send_message("Choose a subcategory for Farmen:", view=view)

    @discord.ui.button(label="Rooftochten", style=discord.ButtonStyle.primary)
    async def rooftochten_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shows subcategory buttons for Rooftochten"""
        view = SubcategoryButtons("rooftochten")  # Subcategories for Rooftochten
        await interaction.response.send_message("Choose a subcategory for Rooftochten:", view=view)

    @discord.ui.button(label="Overig", style=discord.ButtonStyle.primary)
    async def overig_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shows information for Overig"""
        await interaction.response.send_message(faq_data["overig"])

# Subcategory buttons
class SubcategoryButtons(discord.ui.View):
    def __init__(self, category):
        super().__init__()
        self.category = category

        # Ensure that only valid categories are processed
        if category not in faq_data:
            raise ValueError(f"Invalid category: {category}")
        
        # Generate subcategory buttons dynamically based on the category
        for subcategory in faq_data[category]:
            button = discord.ui.Button(label=subcategory.capitalize(), style=discord.ButtonStyle.primary, custom_id=subcategory)
            self.add_item(button)

    # Handle subcategory button clicks
    @discord.ui.button(label="Placeholder", style=discord.ButtonStyle.secondary, custom_id="placeholder", disabled=True)
    async def placeholder_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure interaction is valid"""
        return True

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Returns to the previous menu"""
        view = ScriptButtons()  # Main category buttons
        await interaction.response.send_message("Going back to the main categories.", view=view)

    async def on_button_click(self, interaction: discord.Interaction):
        """Handles button click for subcategories"""
        subcategory = interaction.data["custom_id"]  # Get subcategory from interaction
        description = faq_data[self.category].get(subcategory, "No information available.")
        
        if description:
            await interaction.response.send_message(description)
        else:
            await interaction.response.send_message("No information available for this subcategory.")

# Event for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}({bot.user.id})')

# Slash command for scripts with Buttons
@bot.tree.command(name="scripts")
async def scripts(interaction: discord.Interaction):
    """Shows buttons for different script categories."""
    try:
        view = ScriptButtons()  # Create the view with buttons
        await interaction.response.send_message("Choose a category to get more information:", view=view)
    except Exception as e:
        print(f"Error sending message: {e}")
        await interaction.response.send_message("Failed to show categories. Please try again later.")

    # Ensure that the bot is syncing slash commands
    await bot.tree.sync()

# Run the bot using the token stored in environment variables
if __name__ == '__main__':
    try:
        bot.run(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        print(f"Error running bot: {e}")
