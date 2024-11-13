import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Modal, TextInput, Select
from fuzzywuzzy import fuzz, process
from main import create_embed

# Dictionary of descriptions for the scripts functionality
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

class ScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="scripts", description="Displays the script categories")
    async def scripts(self, interaction: Interaction):
        embed = create_embed("Scripts Menu", "Main menu for scripts")
        await interaction.response.send_message(embed=embed, view=PublicMenuView(self.bot), ephemeral=True)
    
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
            embed = create_embed(f"**{category} scripts:**", "")
            await interaction.response.edit_message(
                content=None,
                embed=embed,
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

        embed = create_embed("Select the script you want more details about:", "")
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )

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
        embed = create_embed(selected_script, description)
        await interaction.response.edit_message(embed=embed, view=self)

    async def search_again(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SearchModal(self.bot))

    async def go_to_main_menu(self, interaction: discord.Interaction):
        embed = create_embed("Scripts Menu", main_menu_description)
        await interaction.response.edit_message(embed=embed, view=PublicMenuView(self.bot))

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
            embed = create_embed(subcategory, description)
            main_menu_only_view = View()
            main_menu_button = Button(label="Main Menu", style=discord.ButtonStyle.danger)
            main_menu_button.callback = self.go_to_main_menu
            main_menu_only_view.add_item(main_menu_button)

            await interaction.response.edit_message(embed=embed, view=main_menu_only_view)
        return callback

    async def go_to_main_menu(self, interaction: discord.Interaction):
        embed = create_embed("Scripts Menu", main_menu_description)
        await interaction.response.edit_message(embed=embed, view=PublicMenuView(self.bot))

async def setup(bot):
    await bot.add_cog(ScriptsCog(bot))

