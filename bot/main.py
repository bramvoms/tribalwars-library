import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Modal, TextInput, Select
from fuzzywuzzy import fuzz, process
import random
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Database of descriptions and scripts
descriptions = {
descriptions = {
    "Offpack": "Offpack is a collection of functionalities to help send attacks efficiently.",
    "TimeTool": "TimeTool helps in accurately timing attacks, allowing for synchronized actions.",
    "SnipeTool": "SnipeTool assists in setting up snipes to defend against incoming attacks.",
    "Defpack": "Defpack organizes defensive troops for optimal distribution in defense.",
    "Mapfunctions": "Mapfunctions provides various tools to enhance the TribalWars map display.",
    "Overwatch": "Overwatch helps monitor villages and activities on the map.",
    "FarmGod": "FarmGod is an automated farming tool to maximize resource gains from farming.",
    "FarmShaper": "FarmShaper organizes and optimizes your farming lists for efficient resource gathering.",
    "Massa rooftochten": "Massa rooftochten simplifies mass scavenging operations for quick loot gathering.",
    "Roof unlocker": "Roof unlocker unlocks the scavenging feature in mass amounts for faster setup.",
    "GS balancer": "GS balancer balances and redistributes resources across villages efficiently.",
    "Noble MS": "Noble MS provides millisecond-level precision for noble timing and coordination.",
    "Troop Counter": "Troop Counter counts and organizes troop levels across all villages.",
    "Sangu Package": "Sangu Package includes a suite of tools to enhance gameplay, like map tools and overviews.",
    "EasyCommand": "EasyCommand simplifies troop command issuing across multiple villages.",
    "CoinPull": "CoinPull maximizes coin minting by redistributing resources where they are needed.",
    "ClaimEnhancer": "ClaimEnhancer adds more features to the village claiming system.",
    "LocalStorage": "LocalStorage saves settings locally for quick access and customization.",
    "marketChecker": "marketChecker scans the market for favorable trades.",
    "TussenStackChecker": "TussenStackChecker helps detect stacking issues between villages.",
    "Toxic Donut's PP Logger": "Logs premium point activity for easy tracking and management.",
    "Coördinaten/DorpsId Converter": "Converts coordinates and village IDs for easier management.",
    "Massameppen met sneltoetsen": "Enables mass attacks using keyboard shortcuts.",
    "Devil's Minting Resource Balancer": "Balances resources for optimized minting across villages.",
    "Duidelijke Milliseconden": "Displays clear millisecond timing in the game interface.",
    "Vlaggen Upgrader": "Automatically upgrades flags across villages based on criteria.",
    "Notities verwijderen via overzicht": "Quickly deletes notes across the game overview.",
    "TW.NL Officiële Extensie": "Official Dutch TribalWars extension with various utilities.",
    "Warenhuis balancer": "Balances resources across warehouses in villages.",
    "Village Renamer By Conquer Date": "Renames villages based on their conquer date.",
    "Munten slaan enhancer": "Enhances the coin minting process for efficiency.",
    "GS balancer (oud)": "An older version of the GS resource balancer.",
    "TribeShare": "TribeShare allows sharing information and maps within the tribe.",
    "Speedtagger": "Tags incoming attacks with speed information for quicker response.",
    "Defteller": "Counts and organizes defensive troops for coordinated defense.",
    "Attack wave recognizer": "Recognizes attack waves and organizes them for analysis.",
    "Dorpnummers intern/extern": "Switches village numbers for internal or external views.",
    "Edelspam sorteer script": "Organizes noble spam attacks for streamlined offense.",
    "Def aanvragen optimalisatie": "Optimizes the process of requesting defensive support.",
    "Renamer van inkomende aanvallen": "Automatically renames incoming attacks for clarity.",
    "Train Spotter": "Detects and organizes incoming train attacks for better defense.",
    "Coord Extractor": "Extracts coordinates from text for easier use.",
    "Farm Enhancer": "Enhances farming tools and reports for better management.",
    "Stamforum update fix": "Fixes issues with tribe forum updates.",
    "GroupPlacer": "Organizes groups for village management.",
    "Server Tijd Font": "Adjusts the server time font for better readability.",
    "QuickFarm": "Quickly manages farming tasks for higher efficiency.",
    "Milliseconden op aanvalsscherm": "Displays milliseconds in the attack screen.",
    "ConfirmEnhancer": "Enhances confirmation dialogs for better user experience.",
    "TimeExport": "Exports time and date information from the game for analysis.",
    "CoAssistent": "Provides assistance with coordinating co-playing responsibilities.",
    "Zet gs in muntverhouding": "Adjusts resource distribution for optimal coin minting.",
    "UnitsDivide": "Divides units among villages for balanced defense and offense.",
    "NobleDivide": "Distributes nobles strategically across villages.",
    "Edelberichten": "Organizes noble-related messages.",
    "TW BB Code ++": "Enhances BB code functionality for use in TribalWars.",
    "CoordFilter": "Filters coordinates for specific criteria.",
    "Village renamer": "Automatically renames villages based on set rules.",
    "GSen opvragen Munten": "Requests resources for minting coins efficiently.",
    "PackageCounter": "Counts and manages package resources.",
    "TW-Surviving troops": "Shows surviving troops after battles.",
    "Vlagfarm log": "Logs flag farming activities.",
    "Single a Farm": "Optimizes single farming tasks.",
    "FA-Pack": "Includes multiple farming assistant tools.",
    "Bevelen Timer in Titel": "Displays command timers in titles for easy tracking.",
    "Devil's Noble Spam Planner Enhancer": "Improves planning for noble spamming strategies.",
    "Cancelsnipen kun je leren": "Helps players learn to cancel snipe attacks.",
    "CommandRenamer": "Renames commands for easier management.",
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
        query = self.query.value.lower()
        results = []

        # Step 1: Exact match check
        if query in descriptions:
            results.append((query, descriptions[query]))
        else:
            # Step 2: Advanced matching with substring and fuzzy matching
            matches = []
            for subcategory, description in descriptions.items():
                subcategory_lower = subcategory.lower()
                description_lower = description.lower()
                
                # Direct substring match
                if query in subcategory_lower or query in description_lower:
                    matches.append((subcategory, description, 90))  # High priority for direct substring matches

                # Fuzzy match with a lower threshold for partial and token set ratios
                elif (fuzz.partial_ratio(query, subcategory_lower) > 50 or fuzz.token_set_ratio(query, subcategory_lower) > 50):
                    score = max(fuzz.partial_ratio(query, subcategory_lower), fuzz.token_set_ratio(query, subcategory_lower))
                    matches.append((subcategory, description, score))  # Priority based on fuzzy score

            # Sort matches by score to prioritize closer matches
            matches = sorted(matches, key=lambda x: x[2], reverse=True)

            # Remove duplicates and keep only the subcategory and description fields
            results = [(subcategory, description) for subcategory, description, _ in dict.fromkeys(matches)]

        # Step 3: Ensure exactly three results by adding random items if needed
        if len(results) < 3:
            additional_results = [
                (subcategory, descriptions[subcategory])
                for subcategory in random.sample(descriptions.keys(), k=min(3 - len(results), len(descriptions)))
                if (subcategory, descriptions[subcategory]) not in results
            ]
            results.extend(additional_results)

        # Only show the top 3 results to keep the output consistent
        await interaction.response.send_message(
            content="Select the script you want more details about:",
            view=ResultSelectionView(results[:3]),  # Show only the top 3 results
            ephemeral=True
        )

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
