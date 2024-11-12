import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from fuzzywuzzy import fuzz
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Updated descriptions dictionary with only the active scripts
descriptions = {
    "Offpack": "Offpack is a collection of functionalities to help send attacks efficiently.",
    "TimeTool": "TimeTool helps in accurately timing attacks, allowing for synchronized actions.",
    "Defpack": "Defpack organizes defensive troops for optimal distribution in defense.",
    "SnipeTool": "SnipeTool assists in setting up snipes to defend against incoming attacks.",
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
}

main_menu_description = """**TribalWars Library: Scripts**

Gebruik de knoppen hieronder om een categorie en daarna het script te selecteren waar je uitleg over wilt."""

class PublicMenuView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
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
            await interaction.response.edit_message(
                content=f"**{category} Subcategories:**",
                embed=None,
                view=PrivateMenuView(self.bot, category)
            )
        return callback

    async def show_search_modal(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SearchModal(self.bot))

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

                # Fuzzy match with a lower threshold
                else:
                    score = max(fuzz.partial_ratio(query, subcategory_lower), fuzz.token_set_ratio(query, subcategory_lower))
                    if score > 50:
                        matches.append((subcategory, description, score))  # Priority based on fuzzy score

            # Sort matches by score to prioritize closer matches
            matches = sorted(matches, key=lambda x: x[2], reverse=True)

            # Remove duplicates and keep only the subcategory and description fields
            results = [(subcategory, description) for subcategory, description, _ in matches]

        # Limit the output to the top 2 results
        top_results = results[:2]

        # Create the view with top results
        view = ResultSelectionView(top_results)

        await interaction.response.edit_message(
            content="Select the script you want more details about:",
            embed=None,
            view=view
        )

class ResultSelectionView(View):
    def __init__(self, results):
        super().__init__(timeout=None)
        self.results = results
        self.add_result_selector()
        # Add "Search Again" button
        self.add_search_again_button()
        # Add "Main Menu" button
        self.add_main_menu_button()

    def add_result_selector(self):
        # Limit descriptions to 100 characters
        options = [
            discord.SelectOption(label=subcategory, description=(description[:97] + "..." if len(description) > 100 else description))
            for subcategory, description in self.results
        ]
        select = Select(placeholder="Choose a script...", options=options)
        select.callback = self.show_description
        self.add_item(select)

    def add_search_again_button(self):
        search_again_button = Button(label="Search Again", style=discord.ButtonStyle.primary)
        search_again_button.callback = self.search_again
        self.add_item(search_again_button)

    def add_main_menu_button(self):
        main_menu_button = Button(label="Main Menu", style=discord.ButtonStyle.danger)
        main_menu_button.callback = self.go_to_main_menu
        self.add_item(main_menu_button)

    async def show_description(self, interaction: discord.Interaction):
        selected_script = interaction.data["values"][0]
        description = descriptions.get(selected_script, "No description available.")
        # Update the message with the script description and keep the current view
        await interaction.response.edit_message(
            content=f"**{selected_script}**:\n{description}",
            embed=None,
            view=self
        )

    async def search_again(self, interaction: discord.Interaction):
        # Reopen the search modal to allow the user to search again
        await interaction.response.send_modal(SearchModal(bot))

    async def go_to_main_menu(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Scripts Menu",
            description=main_menu_description,
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=PublicMenuView(self.bot)
        )

class PrivateMenuView(View):
    def __init__(self, bot, category):
        super().__init__(timeout=None)
        self.bot = bot
        self.category = category
        self.add_category_buttons()
        self.add_main_menu_button()

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

    def add_main_menu_button(self):
        main_menu_button = Button(label="Main Menu", style=discord.ButtonStyle.danger)
        main_menu_button.callback = self.go_to_main_menu
        self.add_item(main_menu_button)

    def show_subcategory_description(self, subcategory):
        async def callback(interaction: discord.Interaction):
            description = descriptions.get(subcategory, "No description available.")
            await interaction.response.edit_message(
                content=f"**{subcategory}**:\n{description}",
                embed=None,
                view=self
            )
        return callback

    async def go_to_main_menu(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Scripts Menu",
            description=main_menu_description,
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=PublicMenuView(self.bot)
        )

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
    view = PublicMenuView(bot)
    await interaction.response.send_message(embed=embed, view=view)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
