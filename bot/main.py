import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed
from discord.ui import View, Button, Modal, TextInput, Select
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Embed color for a consistent style
embed_color = discord.Color.from_rgb(255, 255, 0)

# Utility function to send an embedded message with a footer
async def send_embed(context_or_interaction, content: str, title: str = "Bot Message", ephemeral: bool = False):
    embed = Embed(title=title, description=content, color=embed_color)
    embed.set_footer(text="Created by Victorious")
    
    if isinstance(context_or_interaction, commands.Context):
        await context_or_interaction.send(embed=embed)
    elif isinstance(context_or_interaction, discord.Interaction):
        await context_or_interaction.response.send_message(embed=embed, ephemeral=ephemeral)

# Updated descriptions dictionary with only the active scripts
descriptions = {
    # Aanval category
    "Offpack": """Een collectie aan functionaliteiten samengebracht in één package.

**Forum topic**
<https://forum.tribalwars.nl/index.php?threads/devils-off-pack.206109/>

**Snellijst code**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Devils-Off-Pack_206109.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "TimeTool": """Tool die helpt bij het nauwkeurig timen van bevelen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/timetool.206574/>
**Snellijst code:**
```js
javascript:

var timeColor = "green";
var waitingColor = "#ff9933";
var noDateColor = "green";
var timeBarWidth = false;

$.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/TimeTool_206574.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "EasyCommand": """Verbeterd gecombineerd overzicht met als doel sneller times, snipes, backtimes ed te vinden.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/easycommand.206303/>
**Snellijst code:**
```js
javascript:

var ECsettings = {
minPop : 12000,
colors_on : true,
colors : {
'offence': '#90ef81',
'defence': '#00FFFF',
'noble': '#FFFF00',
'none': '#F4E4BC'
}
};

$.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/EasyCommand_206303.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "NobleSpam": """Script om het plannen via https://devilicious.dev/ sneller te maken.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/devils-noble-spam-planner-enhancer.206110/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Devils-Noble-Spam-Planner-Enhancer_206110.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Template Enhancer": """Templates dynamisch toevoegen aan grote offpack planningen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/toxic-donuts-template-enhancer.207122/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Toxic-Donuts-Template-Enhancer._207122.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "MobileAttSent": """Mobiele attack enhancer die helpt om geen fouten te maken bij het mobiel versturen van planningen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/toxic-donuts-mobile-attack-enhancer.208673/>
**Snellijst code:**
```js
javascript:
var timeGap = false;

$.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Toxic-Donuts-Mobile-Attack-Enhancer_208673_rw6i55c8.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Verdediging category
    "Defpack": """A collection of defensive utils (e.g. Stack health and wall health, incomings overview enhancements)
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/devils-def-pack.206163/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Devils-Def-Pack_206163.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "SnipeTool": """Het script helpt je snel zoeken naar snipe mogelijkheden op verschillende pagina's.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/toxic-donuts-snipe-calculator.206313/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Toxic-Donuts-Snipe-Calculator._206313.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "IncsEnhancer": """Verstuur incomings van jezelf naar een database en zorg dat stamgenoten/vrienden deze kunnen bekijken om makkelijker mee te snipen. 
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/toxic-donuts-incomings-enhancer.207109/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Toxic-Donuts-incomings-enhancer._207109_4265usvb.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "TribeIncs": """Een script dat de incomings van je stamleden laat zien in 1 gemakkelijk overzichtje.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/tribe-members-incoming-overview.205832/>
**Snellijst code:**
```js
javascript:
var shouldRedirect = false;
$.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Tribe-Members-Incoming-Overview_205832.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "UnitsDivide": """Deelt aanwezige troepen in het dorp door het gevraagde aantal en vult deze in.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/unitsdivide.206400/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/UnitsDivide_206400.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Kaart category
    "Mapfunctions": """Collectie van kleine functionaliteiten op de kaart.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/mapfunctions.206294/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/MapFunctions_206294.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Overwatch": """Overwatch - visueel data van de stam op de kaart
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/overwatch.206196/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Overwatch_206196.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "CoordGrab": """Het selecteren van dorpen op de kaart.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/coordgrabber.206127/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/CoordGrabber_206127.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "TribeLines": """Toont op de ingame kaart stam edellijnen die ingegeven worden op het forum.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/tribelines.206290/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/TribeLines_206290.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "ClaimEnhancer": """Dorpen claimen met 1 klik op de kaart of dorpen massaal claimen aan de hand van coords.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/claimenhancer.206296/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/ClaimEnhancer_206296.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Farmen category
    "FarmGod": """Snel en efficiënt versturen van micro farms!
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/farmgod.208446/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/FarmGod_208446.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "FarmShaper": """Easy barbaren dorpen shapen
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/farmshaper.206157/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/FarmShaper_206157.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Rooftochten category
    "Massa rooftochten": """Massa rooftochten script
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/massa-rooftochten.206191/>
**Snellijst code:**
```js
javascript:
var premiumBtnEnabled = false;
$.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Massa-rooftochten_206191.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Roof unlocker": """Snel en eenvoudig RT's unlocken.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/toxic-donuts-scavenge-unlocking-tool.207420/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Toxic-Donuts-Scavenge-Unlocking-Tool._207420.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Overig category
    "GS balancer": """Balanceren van grondstoffen tussen je dorpen
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/gs-balancer.207166/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/GS-Balancer_207166_88qrx570.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "TribeShare": """Deel allerhande informatie snel en overzichtelijk met je stamgenoten en vrienden.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/tribeshare.206804/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/TribeShare_206804_anu64me9.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "CoordFilter": """Script om coördinaten mee te filteren
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/coordfilter.206247/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/CoordFilter_206247.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Resource sender": """Verstuurd grondstoffen in munt verhouding vanuit het huidige dorp naar een gewenst ander dorp.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/gstotargetvillage.207833/>
**Snellijst code:**
```js
javascript:
var targetVillage = [473,431];
var GMprijs = [56000,60000,50000];
var HandelarenThuisLaten = 0;
$.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/GsToTargetVillage_207833_342g9meb.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Village renamer": """Hiermee kan je je dorpsnamen veranderen.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/village-renamer.206245/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Village-renamer_206245.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "GroupPlacer": """Group placer die beschikbaar is op elk scherm.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/toxic-donuts-group-placer.208611/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Toxic-Donuts-Group-Placer_208611.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "ClearsTimer": """Toont je wanneer hoeveel clears klaar zijn.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/remaining-build-time-clears.206135/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Remaining-build-time-clears_206135.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "MintTimer": """Zie eenvoudig en snel wanneer je opslag overloopt op de massa meppen pagina.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/minttimer.207014/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/MintTimer_207014.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "CoinPull": """Script om GS te trekken naar je muntdorp waar vlaggenbooster aan staat.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/coinpull.206367/>
**Snellijst code:**
```js
javascript:
var mintVillages = {'123|456' : 0};
$.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/CoinPull_206367.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Munt Enhancer": """Scriptje dat een timer toevoegt wanneer de opslag vol zou lopen met 1 van de resources.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/munten-slaan-enhancer.205833/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Munten-slaan-enhancer_205833.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Vlaggen upgrader": """Scriptje waar je kan aanduiden hoeveel vlaggen je wil upgraden door gewoon enter ingedrukt te houden.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/vlaggen-upgrader.206619/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Vlaggen-Upgrader_206619.js');
```
Placeholder tekst voor uitgebreide uitleg
""",
    
    # Stats category
    "Noble MS": """Deze JavaScript-code berekent het gemiddelde aantal milliseconden van zichtbare bevelen (nobles) op een webpagina en toont het resultaat met
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/noble-ms.209666/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/noble_ms.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "Troop Counter": """Updated troepen counter
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/troop-counter.206111/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Troop-Counter_206111.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    "PP Log": """Krijg een PP overzicht voor alle werelden.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/toxic-donuts-pp-logger.208854/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Toxic-Donuts-PP-Logger_208854.js');
```
Placeholder tekst voor uitgebreide uitleg
""",

    # Package category
    "Sangu Package": """Het is een verzameling van scripts die de bestaande TW pagina's gaan verrijken door extra informatie.
**Forum topic:** <https://forum.tribalwars.nl/index.php?threads/sangu-package.206130/>
**Snellijst code:**
```js
javascript: $.getScript('https://media.innogamescdn.com/com_DS_NL/scripts/Sangu-Package_206130.js');
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
        categories = ["Must haves", "Aanval", "Verdediging", "Kaart", "Farmen", "Rooftochten", "Overig", "Stats", "Package"]
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
            await send_embed(interaction, "", title=f"{category} scripts", ephemeral=True)
            await interaction.response.edit_message(
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

        if query in descriptions:
            results.append((query, descriptions[query]))
        else:
            matches = []
            for subcategory, description in descriptions.items():
                subcategory_lower = subcategory.lower()
                description_lower = description.lower()

                if query in subcategory_lower or query in description_lower:
                    matches.append((subcategory, description, 90))

                else:
                    score = max(fuzz.partial_ratio(query, subcategory_lower), fuzz.token_set_ratio(query, subcategory_lower))
                    if score > 50:
                        matches.append((subcategory, description, score))

            matches = sorted(matches, key=lambda x: x[2], reverse=True)
            results = [(subcategory, description) for subcategory, description, _ in matches]

        top_results = results[:2]
        view = ResultSelectionView(self.bot, top_results)
        await send_embed(interaction, "Select the script you want more details about:", ephemeral=True)
        await interaction.response.edit_message(view=view)

class ResultSelectionView(View):
    def __init__(self, bot, results):
        super().__init__(timeout=None)
        self.bot = bot
        self.results = results
        self.add_result_selector()
        self.add_search_again_button()
        self.add_main_menu_button()

    def add_result_selector(self):
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
        await send_embed(interaction, description, title=selected_script, ephemeral=True)

    async def search_again(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SearchModal(self.bot))

    async def go_to_main_menu(self, interaction: discord.Interaction):
        await send_embed(interaction, main_menu_description, title="Scripts Menu", ephemeral=True)
        await interaction.response.edit_message(view=PublicMenuView(self.bot))

class PrivateMenuView(View):
    def __init__(self, bot, category):
        super().__init__(timeout=None)
        self.bot = bot
        self.category = category
        self.add_category_buttons()
        self.add_main_menu_button()

    def add_category_buttons(self):
        subcategories = {
            "Must haves": [
                "Offpack", "Defpack", "TimeTool", "Massa rooftochten", "GS balancer", 
                "SnipeTool", "IncsEnhancer", "TribeShare", "NobleSpam", "CoordFilter", 
                "Coordgrab", "Resource sender", "TribeLines", "Village renamer",
                "MintTimer", "CoinPull", "Munt Enhancer", "Template Enhancer",
                "GroupPlacer", "ClearsTimer", "UnitsDivide"
            ],
            "Aanval": ["Offpack", "TimeTool", "EasyCommand", "NobleSpam", "Template Enhancer", "MobileAttSent"],
            "Verdediging": ["Defpack", "SnipeTool", "TimeTool", "IncsEnhancer", "TribeIncs", "UnitsDivide"],
            "Kaart": ["Mapfunctions", "Overwatch", "CoordGrab", "TribeLines", "ClaimEnhancer"],
            "Farmen": ["FarmGod", "FarmShaper"],
            "Rooftochten": ["Massa rooftochten", "Roof unlocker"],
            "Overig": ["GS balancer", "TribeShare", "CoordFilter", "Resource sender", "Village renamer", "GroupPlacer", "ClearsTimer", "MintTimer", "CoinPull", "Munt Enhancer", "Vlaggen upgrader"],
            "Stats": ["Noble MS", "Troop Counter", "PP Log"],
            "Package": ["Sangu Package"],
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
            await send_embed(interaction, description, title=subcategory, ephemeral=True)
        return callback

    async def go_to_main_menu(self, interaction: discord.Interaction):
        await send_embed(interaction, main_menu_description, title="Scripts Menu", ephemeral=True)
        await interaction.response.edit_message(view=PublicMenuView(self.bot))

# Purge command with embedded response
@bot.tree.command(name="purge", description="Purge messages in a channel based on various criteria.")
@app_commands.default_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await send_embed(interaction, "You do not have permission to use this command.", title="Error", ephemeral=True)
        return

    await send_embed(interaction, "Choose a purge option:", title="Purge Options", ephemeral=True)
    await interaction.response.edit_message(view=PurgeOptionsView())

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
        total_deleted = 0
        delay_between_deletions = 1
        command_message_id = interaction.id

        async for message in interaction.channel.history(limit=None):
            if message.id == command_message_id:
                continue

            try:
                await message.delete()
                total_deleted += 1
                await asyncio.sleep(delay_between_deletions)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after or 10
                    await asyncio.sleep(retry_after)
                else:
                    break

        await send_embed(interaction, f"Deleted {total_deleted} messages.", title="Purge Complete", ephemeral=True)

    async def prompt_number_of_messages(self, interaction: discord.Interaction):
        modal = NumberInputModal()
        await interaction.response.send_modal(modal)

    async def purge_non_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        total_deleted = 0
        delay_between_deletions = 1
        command_message_id = interaction.id

        async for message in interaction.channel.history(limit=None):
            if message.id == command_message_id or message.author.bot:
                continue

            try:
                await message.delete()
                total_deleted += 1
                await asyncio.sleep(delay_between_deletions)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after or 10
                    await asyncio.sleep(retry_after)
                else:
                    break

        await send_embed(interaction, f"Deleted {total_deleted} non-bot messages.", title="Purge Complete", ephemeral=True)

    async def purge_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        total_deleted = 0
        delay_between_deletions = 1
        command_message_id = interaction.id

        async for message in interaction.channel.history(limit=None):
            if message.id == command_message_id or not message.author.bot:
                continue

            try:
                await message.delete()
                total_deleted += 1
                await asyncio.sleep(delay_between_deletions)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after or 10
                    await asyncio.sleep(retry_after)
                else:
                    break

        await send_embed(interaction, f"Deleted {total_deleted} bot messages.", title="Purge Complete", ephemeral=True)

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
            deleted_count = 0
            command_message_id = interaction.id

            async for message in interaction.channel.history(limit=limit + 1):
                if message.id == command_message_id:
                    continue

                if deleted_count < limit:
                    try:
                        await message.delete()
                        deleted_count += 1
                    except discord.HTTPException as e:
                        if e.status == 429:
                            retry_after = e.retry_after or 10
                            await asyncio.sleep(retry_after)
                        else:
                            break
                else:
                    break

            await send_embed(interaction, f"Deleted {deleted_count} messages.", title="Purge Complete", ephemeral=True)

        except ValueError:
            await send_embed(interaction, "Please enter a valid positive integer.", title="Error", ephemeral=True)

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
            await send_embed(interaction, f"Deleted {len(deleted)} messages from {user.display_name}.", title="Purge Complete", ephemeral=True)
        except Exception as e:
            await send_embed(interaction, f"Error: {str(e)}", title="Error", ephemeral=True)

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
            await send_embed(interaction, f"Deleted {len(deleted)} messages from the last {hours} hours and {minutes} minutes.", title="Purge Complete", ephemeral=True)
        except ValueError as e:
            await send_embed(interaction, str(e), title="Error", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()

@bot.tree.command(name="scripts", description="Displays the script categories")
async def scripts(interaction: discord.Interaction):
    # Send both the embed and the view in a single response
    await send_embed(interaction, main_menu_description, title="Scripts Menu", ephemeral=True)
    # Send the view along with the embed in the same response to avoid double responding
    await interaction.followup.send(view=PublicMenuView(bot), ephemeral=True)

@bot.command(name="scripts", help="Displays the description of a specific script by name.")
async def get_script_description(ctx, *, script_name: str):
    script_name = script_name.lower()
    matching_script = next((name for name in descriptions if name.lower() == script_name), None)

    if matching_script:
        await send_embed(ctx, descriptions[matching_script], title=matching_script)
    else:
        result = process.extractOne(script_name, descriptions.keys())
        if result:
            closest_match, score = result
            if score > 60:
                view = View()
                suggestion_button = Button(label=f"Bedoelde je '{closest_match}'?", style=discord.ButtonStyle.primary)

                async def suggestion_callback(interaction: discord.Interaction):
                    await send_embed(interaction, descriptions[closest_match], title=closest_match)

                suggestion_button.callback = suggestion_callback
                view.add_item(suggestion_button)

                await send_embed(ctx, f"Script '{script_name}' not found.", title="Script Not Found")
            else:
                await send_embed(ctx, f"Script '{script_name}' not found in the library.", title="Script Not Found")
        else:
            await send_embed(ctx, f"Script '{script_name}' not found in the library.", title="Script Not Found")

class AMView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_button("Opslag rush", self.opslag_rush_callback)
        self.add_button("ZC rush", self.zc_rush_callback)
        self.add_button("AH rush", self.ah_rush_callback)
        self.add_button("Muur rush", self.muur_rush_callback)
        self.add_button("Toren rush", self.toren_rush_callback)
        self.add_button("Kerk rush", self.kerk_rush_callback)
        self.add_button("Muur spoed", self.muur_spoed_callback)
        self.add_button("OFF sjabloon", self.off_sjabloon_callback)
        self.add_button("DEF sjabloon", self.def_sjabloon_callback)

    def add_button(self, label, callback):
        button = Button(label=label, style=discord.ButtonStyle.primary)
        button.callback = callback
        self.add_item(button)

    async def opslag_rush_callback(self, interaction: Interaction):
        await send_embed(interaction, "Placeholder text for Opslag rush.", title="Opslag rush", ephemeral=True)

    async def zc_rush_callback(self, interaction: Interaction):
        await send_embed(interaction, "Placeholder text for ZC rush.", title="ZC rush", ephemeral=True)

    async def ah_rush_callback(self, interaction: Interaction):
        await send_embed(interaction, "Placeholder text for AH rush.", title="AH rush", ephemeral=True)

    async def muur_rush_callback(self, interaction: Interaction):
        await send_embed(interaction, "Placeholder text for Muur rush.", title="Muur rush", ephemeral=True)

    async def toren_rush_callback(self, interaction: Interaction):
        await send_embed(interaction, "Placeholder text for Toren rush.", title="Toren rush", ephemeral=True)

    async def kerk_rush_callback(self, interaction: Interaction):
        await send_embed(interaction, "Placeholder text for Kerk rush.", title="Kerk rush", ephemeral=True)

    async def muur_spoed_callback(self, interaction: Interaction):
        await send_embed(interaction, "Placeholder text for Muur spoed.", title="Muur spoed", ephemeral=True)

    async def off_sjabloon_callback(self, interaction: Interaction):
        await send_embed(interaction, "Placeholder text for OFF sjabloon.", title="OFF sjabloon", ephemeral=True)

    async def def_sjabloon_callback(self, interaction: Interaction):
        await send_embed(interaction, "Placeholder text for DEF sjabloon.", title="DEF sjabloon", ephemeral=True)

@bot.tree.command(name="am", description="Displays rush and template options for AM")
async def am(interaction: Interaction):
    await send_embed(interaction, "Select one of the options below for more information.", title="Choose an action:", ephemeral=True)
    await interaction.response.edit_message(view=AMView(), ephemeral=True)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
