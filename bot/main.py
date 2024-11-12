import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Modal, TextInput, Select
from fuzzywuzzy import fuzz, process
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Database of descriptions and scripts
descriptions = {
    "Offpack": """Offpack is een verzameling van meerdere functionaliteiten die samen komen tot één script die je helpt bij het versturen van aanvallen.""",
    "TimeTool": """TimeTool: Helps in accurately timing attacks.""",
    "Defpack": """Defpack: Organizes defensive troops for optimal defense.""",
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

        # Check for exact match first
        if query in descriptions:
            results.append((query, descriptions[query]))
        else:
            # Use fuzzy matching to find the best matches with a threshold
            matches = process.extract(query, descriptions.keys(), limit=5, scorer=fuzz.partial_ratio)
            results = [(subcategory, descriptions[subcategory]) for subcategory, score in matches if score > 60]

        if results:
            await interaction.response.send_message(
                content="Select the script you want more details about:",
                view=ResultSelectionView(results),
                ephemeral=True
            )
        else:
            await interaction.response.send_message("No matching scripts found.", ephemeral=True)

class ResultSelectionView(View):
    def __init__(self, results):
        super().__init__()
        self.results = results
        self.add_result_selector()

    def add_result_selector(self):
        # Limit descriptions to 100 characters
        options = [
            discord.SelectOption(label=subcategory, description=(description[:97] + "..." if len(description) > 100 else description))
            for subcategory, description in self.results
        ]
        select = Select(placeholder="Choose a script...", options=options)
        select.callback = self.show_description
        self.add_item(select)

    async def show_description(self, interaction: discord.Interaction):
        selected_script = interaction.data["values"][0]
        description = descriptions.get(selected_script, "No description available.")
        await interaction.response.send_message(f"**{selected_script}**:\n{description}", ephemeral=True)

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
