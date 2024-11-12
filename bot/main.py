import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from discord import app_commands
from fuzzywuzzy import fuzz
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Updated descriptions dictionary with only the active scripts
descriptions = {
    # Aanvallen category
    "Offpack": """Een collectie aan functionaliteiten samengebracht in één package.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/devils-off-pack.206109/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Devils-Off-Pack_206109.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "TimeTool": """Helpt bij het nauwkeurig timen van aanvallen en synchroniseren van acties.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/time-tool.206111/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/TimeTool_206111.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "EasyCommand": """Verhoogt de snelheid van het verzenden van commando's over meerdere dorpen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/easycommand.206130/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/EasyCommand_206130.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "NobleSpam": """Automatiseert het versturen van adellijke aanvallen om meerdere dorpen snel te veroveren.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/noblespam.206117/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/NobleSpam_206117.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Template Enhancer": """Verbetert sjablonen voor het organiseren van je dorpen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/template-enhancer.206126/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/TemplateEnhancer_206126.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "MobileAttSent": """Verstuurt aanvallen vanaf je mobiel voor snellere acties.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/mobileattsent.206140/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/MobileAttSent_206140.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Verdeden category
    "Defpack": """Een verzameling van tools die helpen bij het organiseren van verdedigingstaken.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/devils-def-pack.206110/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Devils-Def-Pack_206110.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "SnipeTool": """Helpt bij het opzetten van snipe-aanvallen om inkomende aanvallen te blokkeren.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/snipetool.206114/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/SnipeTool_206114.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "IncsEnhancer": """Verbetert het overzicht van inkomende aanvallen, waardoor je ze snel kunt beheren.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/incs-enhancer.206115/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/IncsEnhancer_206115.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "TribeIncs": """Een tool voor het beheren van inkomende aanvallen binnen je stam.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/tribeincs.206150/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/TribeIncs_206150.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Kaart category
    "Mapfunctions": """Verbetert de functionaliteit van de kaart in het spel.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/mapfunctions.206155/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Mapfunctions_206155.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Overwatch": """Helpt bij het monitoren van dorpen en activiteiten op de kaart.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/overwatch.206160/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Overwatch_206160.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "CoordGrab": """Verzamelt coördinaten automatisch uit tekst voor eenvoudig gebruik.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/coordgrab.206165/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/CoordGrab_206165.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "TribeLines": """Voegt een stam coördinatie functie toe aan je account.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/tribelines.206121/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/TribeLines_206121.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "ClaimEnhancer": """Verbetert de claims op de kaart door extra informatie weer te geven.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/claimenhancer.206170/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/ClaimEnhancer_206170.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Farmen category
    "FarmGod": """Automatiseert het verzamelen van middelen door het efficiënt beheren van boerderijen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/farmgod.206175/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/FarmGod_206175.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "FarmShaper": """Organiseert en optimaliseert je boerderij lijsten voor efficiënter verzamelen van middelen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/farmshaper.206180/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/FarmShaper_206180.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Rooftochten category
    "Massa rooftochten": """Automatiseert het verzenden van massale rooftochten naar meerdere dorpen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/massa-rooftochten.206112/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Massa-Rooftochten_206112.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Roof unlocker": """Maakt het mogelijk om het rooftochten-systeem voor meerdere dorpen snel te ontgrendelen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/roof-unlocker.206185/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/RoofUnlocker_206185.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Overig category
    "GS balancer": """Balanceren en herverdelen van grondstoffen over je dorpen voor optimale efficiëntie.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/gs-balancer.206113/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/GS-Balancer_206113.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "TribeShare": """Maakt het delen van informatie en kaarten binnen je stam eenvoudiger.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/tribeshare.206116/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/TribeShare_206116.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "CoordFilter": """Filtert coördinaten op basis van opgegeven criteria.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/coordfilter.206118/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/CoordFilter_206118.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Resource sender": """Verstuurt grondstoffen tussen dorpen op basis van de behoeften.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/resourcesender.206120/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/ResourceSender_206120.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Village renamer": """Hernamt dorpen automatisch op basis van ingestelde regels.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/villagerenamer.206122/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/VillageRenamer_206122.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "GroupPlacer": """Organiseert groepen voor dorpsbeheer.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/groupplacer.206127/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/GroupPlacer_206127.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "ClearsTimer": """Toont de resterende tijd voor aanvallen of verdedigingen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/clearstimer.206128/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/ClearsTimer_206128.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "MintTimer": """Een timer voor het bijhouden van muntproductie.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/minttimer.206185/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/MintTimer_206185.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "CoinPull": """Maximaliseert muntproductie door grondstoffen te verdelen waar nodig.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/coinpull.206186/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/CoinPull_206186.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Munt Enhancer": """Optimaliseert de muntproductie in het spel.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/munt-enhancer.206187/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/MuntEnhancer_206187.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Stats category
    "Noble MS": """Verhoogt de precisie van adellijke aanvallen door milliseconde-timing.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/noble-ms.206130/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/NobleMS_206130.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Troop Counter": """Houdt de sterkte van je troepen in de gaten en organiseert ze.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/troop-counter.206135/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/TroopCounter_206135.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "PP Log": """Logt premium punt activiteit voor eenvoudig beheer.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/pp-log.206136/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/PPLog_206136.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Package category
    "Sangu Package": """Een pakket van hulpmiddelen die het spel verbeteren.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/sangu-package.206140/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/SanguPackage_206140.js');
```
Placeholder tekst voor uitgebreide uitleg
"""
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
        categories = ["Aanvallen", "Verdedigen", "Kaart", "Farmen", "Rooftochten", "Overig", "Stats", "Package", "Must haves"]
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
        view = ResultSelectionView(self.bot, top_results)

        await interaction.response.edit_message(
            content="Select the script you want more details about:",
            embed=None,
            view=view
        )

class ResultSelectionView(View):
    def __init__(self, bot, results):
        super().__init__(timeout=None)
        self.bot = bot  # Store the bot instance
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
        await interaction.response.send_modal(SearchModal(self.bot))

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
            "Aanvallen": ["Offpack", "TimeTool", "EasyCommand", "NobleSpam", "Template Enhancer", "MobileAttSent"],
            "Verdedigen": ["Defpack", "SnipeTool", "TimeTool", "IncsEnhancer", "TribeIncs"],
            "Kaart": ["Mapfunctions", "Overwatch", "CoordGrab", "TribeLines", "ClaimEnhancer"],
            "Farmen": ["FarmGod", "FarmShaper"],
            "Rooftochten": ["Massa rooftochten", "Roof unlocker"],
            "Overig": ["GS balancer", "TribeShare", "CoordFilter", "Resource sender", "Village renamer", "GroupPlacer", "ClearsTimer", "MintTimer", "CoinPull", "Munt Enhancer"],
            "Stats": ["Noble MS", "Troop Counter", "PP Log"],
            "Package": ["Sangu Package"],
            # Added Must haves category with the specified scripts
            "Must haves": [
                "Offpack", "Defpack", "TimeTool", "Massa rooftochten", "GS balancer", 
                "SnipeTool", "IncsEnhancer", "TribeShare", "NobleSpam", "CoordFilter", 
                "Coordgrab", "Resource sender", "TribeLines", "Village renamer",
                "MintTimer", "CoinPull", "Munt Enhancer", "Template Enhancer",
                "GroupPlacer", "ClearsTimer"
            ]
        }

        # Loop through the categories and add their subcategory buttons
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

# Add the purge command
@bot.tree.command(name="purge", description="Purge messages in a channel based on various criteria.")
@app_commands.default_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction):
    # Check if the user is an administrator
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    # Present options to the user
    view = PurgeOptionsView()
    await interaction.response.send_message("Choose a purge option:", view=view, ephemeral=True)

class PurgeOptionsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Purge All Messages", value="purge_all", description="Delete all messages in the channel."),
            discord.SelectOption(label="Purge Number of Messages", value="purge_number", description="Delete a specific number of messages."),
            discord.SelectOption(label="Purge Non-Bot Messages", value="purge_non_bot", description="Delete all messages sent by users."),
            discord.SelectOption(label="Purge Bot Messages", value="purge_bot", description="Delete all messages sent by bots."),
            discord.SelectOption(label="Purge Messages from a User", value="purge_user", description="Delete messages from a specific user."),
            discord.SelectOption(label="Purge Messages from a Timeframe", value="purge_timeframe", description="Delete messages within a timeframe."),
        ]
        super().__init__(placeholder="Select a purge option...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        option = self.values[0]
        if option == "purge_all":
            await self.view.purge_all_messages(interaction)
        elif option == "purge_number":
            await self.view.prompt_number_of_messages(interaction)
        elif option == "purge_non_bot":
            await self.view.purge_non_bot_messages(interaction)
        elif option == "purge_bot":
            await self.view.purge_bot_messages(interaction)
        elif option == "purge_user":
            await self.view.prompt_user_selection(interaction)
        elif option == "purge_timeframe":
            await self.view.prompt_timeframe(interaction)

class PurgeOptionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PurgeOptionsSelect())

    async def purge_all_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        deleted = await interaction.channel.purge()
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

    async def prompt_number_of_messages(self, interaction: discord.Interaction):
        modal = NumberInputModal()
        await interaction.response.send_modal(modal)

    async def purge_non_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        deleted = await interaction.channel.purge(limit=None, check=lambda m: not m.author.bot)
        await interaction.followup.send(f"Deleted {len(deleted)} non-bot messages.", ephemeral=True)

    async def purge_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        deleted = await interaction.channel.purge(limit=None, check=lambda m: m.author.bot)
        await interaction.followup.send(f"Deleted {len(deleted)} bot messages.", ephemeral=True)

    async def prompt_user_selection(self, interaction: discord.Interaction):
        modal = UserSelectionModal()
        await interaction.response.send_modal(modal)

    async def prompt_timeframe(self, interaction: discord.Interaction):
        modal = TimeframeModal()
        await interaction.response.send_modal(modal)

class NumberInputModal(discord.ui.Modal, title="Purge Number of Messages"):
    number = TextInput(label="Number of messages to delete", placeholder="Enter a number (e.g., 10)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.number.value)
            if limit <= 0:
                raise ValueError("Number must be positive.")
            await interaction.response.defer(thinking=True)
            deleted = await interaction.channel.purge(limit=limit)
            await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Please enter a valid positive integer.", ephemeral=True)

class UserSelectionModal(discord.ui.Modal, title="Purge Messages from a User"):
    user_input = TextInput(label="User ID or Mention", placeholder="Enter the user's ID or mention them", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_value = self.user_input.value.strip()
            user = None
            if user_value.isdigit():
                user = await interaction.guild.fetch_member(int(user_value))
            elif user_value.startswith("<@") and user_value.endswith(">"):
                user_id = int(user_value.strip("<@!>"))
                user = await interaction.guild.fetch_member(user_id)
            else:
                user = interaction.guild.get_member_named(user_value)
            if user is None:
                raise ValueError("User not found.")

            await interaction.response.defer(thinking=True)
            deleted = await interaction.channel.purge(limit=None, check=lambda m: m.author == user)
            await interaction.followup.send(f"Deleted {len(deleted)} messages from {user.display_name}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

class TimeframeModal(discord.ui.Modal, title="Purge Messages from a Timeframe"):
    hours = TextInput(label="Hours", placeholder="Enter the number of hours", required=False)
    minutes = TextInput(label="Minutes", placeholder="Enter the number of minutes", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            hours = int(self.hours.value) if self.hours.value else 0
            minutes = int(self.minutes.value) if self.minutes.value else 0
            if hours == 0 and minutes == 0:
                raise ValueError("Please enter a valid timeframe.")

            from datetime import datetime, timedelta

            time_limit = datetime.utcnow() - timedelta(hours=hours, minutes=minutes)

            await interaction.response.defer(thinking=True)
            deleted = await interaction.channel.purge(after=time_limit)
            await interaction.followup.send(f"Deleted {len(deleted)} messages from the last {hours} hours and {minutes} minutes.", ephemeral=True)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)

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
