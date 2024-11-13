import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button
from fuzzywuzzy import process  # Import for fuzzy matching
from main import create_embed

# Dictionary of descriptions for the AM functionality
am_descriptions = {
    "Opslag rush": """Bouw sjabloon om zo snel mogelijk opslagplaats level 30 en marktplaats level 25 te bouwen.
    
    📁 - **TEMPLATE**
    vAAAAQ8BEAERAQkBEAEAAQABCwEMAQ0BDgEPARABAAEAAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABDwEQAQABEAEAARABAAEQAQABEAEQAQABDwEPAQ8BDwELAQsBCwELAQsBCwELAQsBCwEPAQ8BCwELAQsBCwELAQ8BDwEPAQsBCwELAQsBCwEQARABEAEQARABEAEQARABCwELAQsBCwELAQAA9ICAgE9wc2xhZyBydXNo9ICAgDQ=
    """,
    "ZC rush": """Bouw sjabloon om zo snel mogelijk ZC te kunnen produceren.
    
    📁 - **TEMPLATE**
    oAAAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABEAEAARABAAEQAQABEAEAARABEAEAARABAAEQAQABEAEAARABAAEQAQABAAEQAQABDwEPAQ8BDwEPAQ8BDwEPAQ8BAQUIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCAECCg8NAAD0gICAWkMgUnVzaPSAgIA0
    """,
    "AH rush": """Bouw sjabloon om een adelshoeve in 8 dagen te bouwen zonder PP inzet en daarna het dorp regulier uit te bouwen.
    
    📁 - **TEMPLATE**
    8gEAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABEAEAARABAAEQAQABEAEAARABEAEAARABAAEQAQABEAEAARABAAEQAQABAAEQAQABDwEPAQ8BDwEPAQ8BDwEPAQ8BAQEIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCAEIAQgBCwELAQsBCwELAQsBCwELAQsBBwEMAQ0BDgENAQ0BDQEMAQ0BDwEPAQ8BDwEQARABEAEQAQEBAQEBAQEBAgECAQIBAwEPAQEBAQEBAQEBAgEPAQEBAgEPAQEBAgEBAQIBDwEBAQIBDwEBAQIBDwEBAQIBDwEBAQIBDwEBAQIBAQECAQ8BDwELAQsBCwELAQsBDwELAQsBCwEPAQsBCwEPAQ8BEAEPARABEAELAQsBCwELAQsBDAENAQwBDQEMAQ0BDAENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgENAQwBDgEMAQ4BDAEOAQIBAgEAAPSAgIBFREVM9ICAgDQ=
    """,
    "Muur rush": """Bouw sjabloon om zo snel mogelijk muur level 20 te hebben.
    
    📁 - **TEMPLATE**
    iAAAAQ8BEAERAQkBEAEAAQABCwEBARABEAEQAQABAAEAAQABEAEAARABAAEQAQABEAEAARABDwEAARABDwEAARABAAEQAQ8BAAEQAQABEAEPARABAAEQAQ8BAAEQAQABDwESARIBEgESARIBEgESARIBEgESARIBEgESARIBEgESARIBEgESARIBAAD0gICATXV1ciBydXNo9ICAgDQ=
    """,
    "Toren rush": """Bouw sjabloon om zo snel mogelijk toren level 20 te hebben.
    
    📁 - **TEMPLATE**
    8AAAARABCQERAQ8BAAEAARABCwEKAQwBDQEOAQ8BDwEAAQABEAEAARABAAEQARABAAEAARABEAEAARABAAEQARABAAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEQAQABDwEPAQ8BDwEPAQ8BDwEPAQ8BDwEPAQ8BEAEGARABBgEQAQYBBgEQAQYBDwEPARABBgEPAQYBDwEQAQYBEAEGAQ8BBgEPAQYBDwEGAQ8BBgEPAQYBDwEGAQ8BBgEQAQ8BBgEPARABBgEPAQYBDwEGAQEBAQEBAQEBAQEIAQgBCAEIAQgBAgEAAPSAgIBUb3JlbiBydXNo9ICAgDQ=
    """,
    "Kerk rush": """Bouw sjabloon om zo snel mogelijk kerk level 3 te hebben.
    
    📁 - **TEMPLATE**
    tgAAARABCQERAQ8BAAEAARABCwEKAQwBDQEOAQ8BDwEAAQABEAEAARABAAEQARABAAEAARABEAEAARABAAEQARABAAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEQAQABDwEPAQ8BDwEPAQ8BDwEPAQ8BDwEPAQ8BDwEPAQ8BDwEPAQ8BBAEPAQ8BDwEEAQ8BDwEEAQEBAQEBAQEBAQEIAQgBCAEIAQgBAgEPAQAA9ICAgEtlcmsgcnVzaPSAgIA0
    """,
    "Muur spoed": """Bouw sjabloon om te gebruiken bij incomings, waar muur zo snel mogelijk opgebouwd moet worden en je potentieel premium punten gebruikt om bouwtijd te verkorten. Hoofdgebouw wordt in dit sjabloon niet geüpgraded.
    
    📁 - **TEMPLATE**
    HAAAARABCQEPAREBEAEAAQABCwEKAQEBDAENARIUAAD0gICATXV1ciBzcG9lZPSAgIA0
    """,
    "OFF sjabloon": """Bouw sjabloon voor offensieve dorpen.
    
    📁 - **TEMPLATE**
    LAIAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABDwEPAQ8BDwEQAQABEAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEAARABAAEPAQ8BDwEPAQ8BAQEBAQEBAQEBAQgBCAEIAQgBCAECAQIBAgEPAQgBCAEIAQgBCAEPAQMBDwEBAQEBAQEBAQIBDwEBAQIBDwEBAQIBAQECAQ8BAQECAQ8BAQECAQ8BAQECAQ8BAQECAQ8BEAEBAQIBAQECAQ8BCwELAQsBCwELAQsBCwELAQsBDwELAQsBCwELAQsBDwELAQsBCwEPAQsBCwEPARABEAEPARABEAEPARABEAELAQsBDwELAQsBDwELAQ8BDAENAQ4BDQENAQ0BDAENAQwBDQEMAQ0BDAENAQwBDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDAEOAQwBDgEIAQgBCAEIAQgBCAEIAQgBCAEIAQcBAQECAQEBAgECAQIBAgECAQIBAQEBAQEBAQEBAQMBAwEDAQMBAwEDAQMBAwEDARIUEQMOAQ4BDgEOAQ4BAAH0gICAQ2FzMTUgfCBPZmZlbnNpZWb0gICANA==
    """,
    "DEF sjabloon": """Bouw sjabloon voor defensieve dorpen.
    
    📁 - **TEMPLATE**
    LAIAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABDwEPAQ8BDwEQAQABEAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEAARABAAEPAQ8BDwEPAQ8BAQEBAQEBAQEBAQgBCAEIAQgBCAECAQ8BAQEBAQEBAQEBAQ8BAQEBAQEBAQEBAQ8BAQEQAQEBAQEPAQ8BCwELAQsBCwELAQsBCwELAQsBDwELAQsBDwELAQsBCwEPAQsBCwEPAQsBCwEPAQsBDwEQARABDwEQARABDwEQARABDwELAQsBCwEPAQsBCwEPAQgBCAEIAQgBCAEDAQgBCAEIAQgBCAEPAQIBAgECAQIBAgECAQIBAgECAQwBDQEOAQ0BDQENAQwBDQEMAQ0BDAENAQwBDQEMAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ8BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDwENAQwBDgENAQwBDgENAQwBDgEPAQ0BDAEOAQ0BDAEOAQ0BDAEOAQwBDgEMAQ4BCAEIAQgBCAEIAQcBAQEBAQEBAQEBAQEBAQECAQIBAgECAQIBAgECAQIBAgECAQMBAwEDAQMBAwEDAQMBAwEDARIUEQMOAQ4BDgEOAQ4BAAH0gICAQ2FzMTUgfCBEZWZlbnNpZWb0gICANA==
    """,
     "Kerk sjabloon": """Bouw sjabloon voor kerk dorpen.
    
    📁 - **TEMPLATE**
    MAIAAQkBDwEQAREBEAEAAQABCwEMAQ0BDgEQARABEAEQARABEAEQARABCgEAAQABAAEAAQABAAEQAQABDwEPAQ8BDwEQAQABEAEAARABAAEQAQABEAEQAQABEAEAARABAAEQAQABEAEAARABAAEAARABAAEPAQ8BDwEPAQ8BAQEBAQEBAQEBAQgBCAEIAQgBCAECAQ8BAQEBAQEBAQEBAQ8BAQEBAQEBAQEBAQ8BAQEQAQEBAQEPAQ8BCwELAQsBCwELAQsBCwELAQsBDwELAQsBDwELAQsBCwEPAQsBCwEPAQsBCwEPAQsBDwEQARABDwEQARABDwEQARABDwELAQsBCwEPAQsBCwEPAQgBCAEIAQgBCAEDAQgBCAEIAQgBCAEPAQIBAgECAQIBAgECAQIBAgECAQwBDQEOAQ0BDQENAQwBDQEMAQ0BDAENAQwBDQEMAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ0BDAEOAQ8BDQEMAQ4BDQEMAQ4BDQEMAQ4BDQEMAQ4BDwENAQwBDgENAQwBDgENAQwBDgEPAQ0BDAEOAQ0BDAEOAQ0BDAEOAQwBDgEMAQ4BCAEIAQgBCAEIAQcBAQEBAQEBAQEBAQEBAQECAQIBAgECAQIBAgECAQIBAgEDAQMBAwEDAQMBAwEDAQMBAwESFBEDDgEOAQ4BDgEOAQQDAwMRAgABBPSAgIBDYXMxNSB8IEtlcmsgbHZsIDP0gICANA==
    """,
    "Toren sjabloon": """Bouw sjabloon voor toren dorpen.
    
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
        title = f"━━━━━━ {subcategory.upper()} ━━━━━━"
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
        embed = create_embed("AM sjablonen", "Selecteer welk sjabloon je wilt bekijken")
        await interaction.response.edit_message(embed=embed, view=self)

class AMCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command to show AM options
    @app_commands.command(name="am", description="Toont het AM sjablonen menu")
    async def am(self, interaction: Interaction):
        embed = create_embed("AM sjablonen", "Selecteer welk sjabloon je wilt bekijken")
        await interaction.response.send_message(embed=embed, view=AMView(self.bot), ephemeral=True)

    # Text command for !am <template_name> for direct template lookup
    @commands.command(name="am", help="Zoek een specifiek AM sjabloon")
    async def get_am_template_description(self, ctx, *, template_name: str):
        template_name = template_name.lower()  # Normalize input to lowercase
        matching_template = am_descriptions.get(template_name)  # Try to find an exact match

        if matching_template:
            # Send the exact match description
            title = f"━━━━━━ {template_name.upper()} ━━━━━━"
            embed = create_embed(title=title, description=matching_template)
            await ctx.send(embed=embed)
        else:
            # No exact match, use fuzzy matching to find the closest template
            closest_match, score = process.extractOne(template_name, am_descriptions.keys())
            
            if score > 60:  # Threshold for considering a match
                # Show the closest match automatically
                title = f"━━━━━━ {closest_match.upper()} ━━━━━━"
                embed = create_embed(title=title, description=am_descriptions[closest_match])
                await ctx.send(embed=embed)
            else:
                # No close match found
                embed = create_embed("Template Not Found", f"No template found matching '{template_name}'.")
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AMCog(bot))
