import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Modal, TextInput
from fuzzywuzzy import fuzz
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Database of descriptions and scripts
descriptions = {
    "Offpack": """Offpack is een verzameling van meerdere functionaliteiten die samen komen tot één script die je helpt bij het versturen van aanvallen.""",
    "TimeTool": """TimeTool: Helps in accurately timing attacks.""",
    # Other descriptions...
}

main_menu_description = """**TribalWars Library: Scripts**

Gebruik de knoppen hieronder om een categorie en daarna het script te selecteren waar je uitleg over wilt."""

class PublicMenuView(View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.add_main_buttons()
        self.add_search_button()

    def add_main_buttons(self):
        categories = ["Aanvallen", "Verdedigen", "Kaart", "Farmen", "Rooftochten", "Overig", "Stats", "Package"]
        for category in categories:
            button = Button(label=category, style=discord.ButtonStyle.primary)
            button.callback = self.show_private_menu(category)
            self.add_item(button)

    def add_search_button(self):
        search_button = Button(label="Search", style=discord.ButtonStyle.secondary)
        search_button.callback = self.show_search_modal
        self.add_item(search_button)

    def show_private_menu(self, category):
        async def callback(interaction: discord.Interaction):
            await interaction.response.send_message(
                content=f"{category} Subcategories:",
                view=PrivateMenuView(self.bot, category),
                ephemeral=True
            )
        return callback

    async def show_search_modal(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SearchModal(bot))

class SearchModal(Modal):
    def __init__(self, bot):
        super().__init__(title="Search Scripts")
        self.bot = bot
        self.query = TextInput(label="Enter script name or keyword", placeholder="e.g., Offpack")
        self.add_item(self.query)

    async def on_submit(self, interaction: discord.Interaction):
        query = self.query.value
        results = []

        # Fuzzy matching to allow minor typos
        for subcategory, description in descriptions.items():
            if fuzz.partial_ratio(query.lower(), subcategory.lower()) > 70 or fuzz.partial_ratio(query.lower(), description.lower()) > 70:
                results.append(f"**{subcategory}**:\n{description}\n")

        if results:
            await interaction.response.send_message("Search Results:\n\n" + "\n".join(results), ephemeral=True)
        else:
            await interaction.response.send_message("No matching scripts found.", ephemeral=True)

class PrivateMenuView(View):
    def __init__(self, bot, category):
        super().__init__()
        self.bot = bot
        self.category = category
        self.add_category_buttons()

    def add_category_buttons(self):
        subcategories = {
            "Aanvallen": ["Offpack", "TimeTool"],
            "Verdedigen": ["Defpack", "SnipeTool"],
            "Kaart": ["Mapfunctions", "Overwatch"],
            "Farmen": ["FarmGod", "FarmShaper"],
            "Rooftochten": ["Massa rooftochten", "Roof unlocker"],
            "Overig": ["GS balancer"],
            "Stats": ["Noble MS", "Troop Counter"],
            "Package": ["Sangu Package", "EasyCommand"]
        }

        for subcategory in subcategories.get(self.category, []):
            button = Button(label=subcategory, style=discord.ButtonStyle.secondary)
            button.callback = self.show_subcategory_description(subcategory)
            self.add_item(button)

        # Add a back button to return to the main menu
        back_button = Button(label="Previous", style=discord.ButtonStyle.danger)
        back_button.callback = self.go_back
        self.add_item(back_button)

    def show_subcategory_description(self, subcategory):
        async def callback(interaction: discord.Interaction):
            description = descriptions.get(subcategory, "No description available.")
            await interaction.response.send_message(f"{subcategory}:\n{description}", ephemeral=True)
        
        return callback

    async def go_back(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=main_menu_description, view=PublicMenuView(self.bot))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()  # Sync commands with Discord

@bot.tree.command(name="scripts", description="Displays the script categories")
async def scripts(interaction: discord.Interaction):
    # Send an embedded message as a regular bot message with a description
    embed = discord.Embed(
        title="Scripts Menu",
        description=main_menu_description,
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=PublicMenuView(bot))

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
