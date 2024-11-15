import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button
from fuzzywuzzy import process  # Import for fuzzy matching
from googletrans import Translator  # Import for translation
from main import create_embed

translator = Translator()  # Initialize translator

# Dictionary of descriptions for the AM functionality
am_descriptions = {
    "Warehouse push": """Construction template to build warehouse level 30 and marketplace level 25 as fast as possible.
    
    📁 - **TEMPLATE**
    vAAAAQ8BEAERAQkBEAEAAQABCwEMAQ0BDgEPARABAAEAAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABDwEQAQABEAEAARABAAEQAQABEAEQAQABDwEPAQ8BDwELAQsBCwELAQsBCwELAQsBCwEPAQ8BCwELAQsBCwELAQ8BDwEPAQsBCwELAQsBCwEQARABEAEQARABEAEQARABCwELAQsBCwELAQAA9ICAgE9wc2xhZyBydXNo9ICAgDQ=
    """,
    "HC rush": """Construction template to produce HC as quickly as possible.
    
    📁 - **TEMPLATE**
    oAAAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABEAEAARABAAEQAQABEAEAARABEAEAARABAAEQAQABEAEAARABAAEQAQABAAEQAQABDwEPAQ8BDwEPAQ8BDwEPAQ8BAQUIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCAECCg8NAAD0gICAWkMgUnVzaPSAgIA0
    """,
    "Academy push": """Construction template to build an academy in 8 days without PP commitment and then build out the village regularly.
    
    📁 - **TEMPLATE**
    8gEAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABEAEAARABAAEQAQABEAEAARABEAEAARABAAEQAQABEAEAARABAAEQAQABAAEQAQABDwEPAQ8BDwEPAQ8BDwEPAQ8BAQEIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCwELAQsBCwELAQsBCwELAQsBBwEMAQ0BDgENAQ0BDQEMAQ0BDwEPAQ8BDwEQARABEAEQAQEBAQEBAQEBAgECAQIBAwEPAQEBAQEBAQEBAgEPAQEBAgEPAQEBAgEBAQIBDwEBAQIBDwEBAQIBDwEBAQIBDwEBAQIBDwEBAQIBAQECAQ8BDwELAQsBCwELAQsBDwELAQsBCwEPAQsBCwEPAQ8BEAEPARABEAELAQsBCwELAQsBDAENAQwBDQEMAQ0BDAENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgEMAQ4BDAEOAQIBAgEAAPSAgIBFREVM9ICAgDQ=
    """,
    "Wall push": """Construction template to have wall level 20 as soon as possible.
    
    📁 - **TEMPLATE**
    iAAAAQ8BEAERAQkBEAEAAQABCwEBARABEAEQAQABAAEAAQABEAEAARABAAEQAQABEAEAARABDwEAARABDwEAARABAAEQAQ8BAAEQAQABEAEPARABAAEQAQ8BAAEQAQABDwESARIBEgESARIBEgESARIBEgESARIBEgESARIBEgESARIBEgESARIBAAD0gICATXV1ciBydXNo9ICAgDQ=
    """,
    "Tower push": """Construction template to have watchtower level 20 as soon as possible.
    
    📁 - **TEMPLATE**
    8AAAARABCQERAQ8BAAEAARABCwEKAQwBDQEOAQ8BDwEAAQABEAEAARABAAEQARABAAEAARABEAEAARABAAEQARABAAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEQAQABDwEPAQ8BDwEPAQ8BDwEPAQ8BDwEPAQ8BEAEGARABBgEQAQYBBgEQAQYBDwEPARABBgEPAQYBDwEQAQYBEAEGAQ8BBgEPAQYBDwEGAQ8BBgEPAQYBDwEGAQ8BBgEQAQ8BBgEPARABBgEPAQYBDwEGAQEBAQEBAQEBAQEIAQgBCAEIAQgBAgEAAPSAgIBUb3JlbiBydXNo9ICAgDQ=
    """,
    "Church push": """Construction template to have church level 3 as soon as possible.
    
    📁 - **TEMPLATE**
    tgAAARABCQERAQ8BAAEAARABCwEKAQwBDQEOAQ8BDwEAAQABEAEAARABAAEQARABAAEAARABEAEAARABAAEQARABAAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEQAQABDwEPAQ8BDwEPAQ8BDwEPAQ8BDwEPAQ8BDwEPAQ8BDwEPAQ8BBAEPAQ8BDwEEAQ8BDwEEAQEBAQEBAQEBAQEIAQgBCAEIAQgBAgEPAQAA9ICAgEtlcmsgcnVzaPSAgIA0
    """,
    "Wall urgent": """Construction template to use with incomings, where wall must be built as quickly as possible and you potentially use premium points to reduce construction time. Headquarters is not upgraded in this template.
    
    📁 - **TEMPLATE**
    HAAAARABCQEPAREBEAEAAQABCwEKAQEBDAENARIUAAD0gICATXV1ciBzcG9lZPSAgIA0
    """,
    "OFF template": """Construction template for offensive villages. Be cautious using this, as this might not suit your style.
    
    📁 - **TEMPLATE**
    LAIAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABDwEPAQ8BDwEQAQABEAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEAARABAAEPAQ8BDwEPAQ8BAQEBAQEBAQEBAQgBCAEIAQgBCAECAQIBAgEPAQgBCAEIAQgBCAEPAQMBDwEBAQEBAQEBAQIBDwEBAQIBDwEBAQIBAQECAQ8BAQECAQ8BAQECAQ8BAQECAQ8BAQECAQ8BEAEBAQIBAQECAQ8BCwELAQsBCwELAQsBCwELAQsBDwELAQsBCwELAQsBDwELAQsBCwEPAQsBCwEPARABEAEPARABEAEPARABEAELAQsBDwELAQsBDwELAQ8BDAENAQ4BDQENAQ0BDAENAQwBDQEMAQ0BDAENAQwBDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDAEOAQwBDgEIAQgBCAEIAQgBCAEIAQgBCAEIAQcBAQECAQEBAgECAQIBAgECAQIBAQEBAQEBAQEBAQMBAwEDAQMBAwEDAQMBAwEDARIUEQMOAQ4BDgEOAQ4BAAH0gICAQ2FzMTUgfCBPZmZlbnNpZWb0gICANA==
    """,
    "DEF template": """Construction template for defensive villages. Be cautious using this, as this might not suit your style.
    
    📁 - **TEMPLATE**
    LAIAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABDwEPAQ8BDwEQAQABEAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEAARABAAEPAQ8BDwEPAQ8BAQEBAQEBAQEBAQgBCAEIAQgBCAECAQ8BAQEBAQEBAQEBAQ8BAQEBAQEBAQEBAQ8BAQEQAQEBAQEPAQ8BCwELAQsBCwELAQsBCwELAQsBDwELAQsBDwELAQsBCwEPAQsBCwEPAQsBCwEPAQsBDwEQARABDwEQARABDwEQARABDwELAQsBCwEPAQsBCwEPAQgBCAEIAQgBCAEDAQgBCAEIAQgBCAEPAQIBAgECAQIBAgECAQIBAgECAQwBDQEOAQ0BDQENAQwBDQEMAQ0BDAENAQwBDQEMAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ8BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDwENAQwBDgENAQwBDgENAQwBDgEPAQ0BDAEOAQ0BDAEOAQ0BDAEOAQwBDgEMAQ4BCAEIAQgBCAEIAQcBAQEBAQEBAQEBAQEBAQECAQIBAgECAQIBAgECAQIBAgECAQMBAwEDAQMBAwEDAQMBAwEDARIUEQMOAQ4BDgEOAQ4BAAH0gICAQ2FzMTUgfCBEZWZlbnNpZWb0gICANA==
    """,
     "Church template": """Construction template for church villages. Be cautious using this, as this might not suit your style.
    
    📁 - **TEMPLATE**
    MAIAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABDwEPAQ8BDwEQAQABEAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEAARABAAEPAQ8BDwEPAQ8BAQEBAQEBAQEBAQgBCAEIAQgBCAECAQ8BAQEBAQEBAQEBAQ8BAQEBAQEBAQEBAQ8BAQEQAQEBAQEPAQ8BCwELAQsBCwELAQsBCwELAQsBDwELAQsBDwELAQsBCwEPAQsBCwEPAQsBCwEPAQsBDwEQARABDwEQARABDwEQARABDwELAQsBCwEPAQsBCwEPAQgBCAEIAQgBCAEDAQgBCAEIAQgBCAEPAQIBAgECAQIBAgECAQIBAgECAQwBDQEOAQ0BDQENAQwBDQEMAQ0BDAENAQwBDQEMAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ8BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDwENAQwBDgENAQwBDgENAQwBDgEPAQ0BDAEOAQ0BDAEOAQ0BDAEOAQwBDgEMAQ4BCAEIAQgBCAEIAQcBAQEBAQEBAQEBAQEBAQECAQIBAgECAQIBAgECAQIBAgEDAQMBAwEDAQMBAwEDAQMBAwESFBEDDgEOAQ4BDgEOAQQDAwMRAgABBPSAgIBDYXMxNSB8IEtlcmsgbHZsIDP0gICANA==
    """,
    "Watchtower template": """Construction template for watchtower villages. Be cautious using this, as this might not suit your style.
    
    📁 - **TEMPLATE**
    CgIAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABDwEPAQ8BDwEQAQABEAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEAARABAAEPAQ8BDwEPAQ8BAQEBAQEBAQEBAQgBCAEIAQgBCAECAQ8BAQEBAQEBAQEBAQ8BAQEBAQEBAQEBAQ8BAQEQAQEBAQEPAQ8BCwELAQsBCwELAQsBCwELAQsBDwELAQsBDwELAQsBCwEPAQsBCwEPAQsBCwEPAQsBDwEQARABDwEQARABDwEQARABDwELAQsBCwEPAQsBCwEPAQgBCAEIAQgBCAEDAQgBCAEIAQgBCAEPAQIBAgECAQIBAgECAQIBAgECAQwBDQEOAQ0BDQENAQwBDQEMAQ0BDAENAQwBDQEMAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ8BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDwENAQwBDgENAQwBDgENAQwBDgEPAQ0BDAEOAQ0BDAEOAQ0BDAEOAQwBDgEMAQ4BCAEIAQgBCAEIAQcBAgECAQIBAgECAQIBAwESFBEDDgEOAQ4BDgEOAQYUEQEAAQQG9ICAgENhczE1IHwgVG9yZW4gbHZsIDIw9ICAgDQ=
    """,
}

class AMView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        for label in am_descriptions.keys():
            button = Button(label=label, style=discord.ButtonStyle.primary)
            button.callback = lambda interaction, label=label: self.show_am_description(interaction, label)
            self.add_item(button)

    async def show_am_description(self, interaction: Interaction, subcategory):
        # Format the title and retrieve description
        title = f"━ {subcategory.upper()} ━"
        description = am_descriptions.get(subcategory, "No description available.")
        embed = create_embed(title=title, description=description)
        
        # Create a main menu button view
        main_menu_only_view = View()
        main_menu_button = Button(label="Main Menu", style=discord.ButtonStyle.danger)
        main_menu_button.callback = self.go_to_main_menu
        main_menu_only_view.add_item(main_menu_button)

        await interaction.response.edit_message(embed=embed, view=main_menu_only_view)

    async def go_to_main_menu(self, interaction: Interaction):
        # Redirect to the main AM menu
        title = f"⚙️ ** AM TEMPLATES ** ⚙️"
        embed = create_embed(title=title, description="Select which template you want to view.\nCopy the text under TEMPLATE and paste it ingame:\nAccount Manager > Construction > Manage templates > Import template.")
        await interaction.response.edit_message(embed=embed, view=self)

class AMCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command to show AM options
    @app_commands.command(name="amtemplates", description="Displays the AM templates menu")
    async def am(self, interaction: Interaction):
        title = f"⚙️ ** AM TEMPLATES ** ⚙️"
        embed = create_embed(title=title, description="Selecteer welk sjabloon je wilt bekijken")
        await interaction.response.send_message(embed=embed, view=AMView(self.bot), ephemeral=True)

    # Text command for &amtemplates <template_name> for direct template lookup
    @commands.command(name="amtemplates", help="Find a specific AM template")
    async def get_am_template_description(self, ctx, *, template_name: str):
        # Translate the input to English
        try:
            translation = translator.translate(template_name, src='auto', dest='en')
            translated_name = translation.text.lower()  # Normalize to lowercase
        except Exception as e:
            await ctx.send(f"Error translating template name: {e}")
            return

        # Try to match the translated name with the English templates
        matching_template = am_descriptions.get(translated_name)  # Exact match

        if matching_template:
            # Send the exact match description
            title = f"━ {translated_name.upper()} ━"
            embed = create_embed(title=title, description=matching_template)
            await ctx.send(embed=embed)
        else:
            # No exact match, use fuzzy matching to find the closest template
            closest_match, score = process.extractOne(translated_name, am_descriptions.keys())
            
            if score > 60:  # Threshold for considering a match
                # Show the closest match automatically
                title = f"━ {closest_match.upper()} ━"
                embed = create_embed(title=title, description=am_descriptions[closest_match])
                await ctx.send(embed=embed)
            else:
                # No close match found
                embed = create_embed("Template Not Found", f"No template found matching '{template_name}' in your language.")
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AMCog(bot))
