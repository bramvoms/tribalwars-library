import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button
from fuzzywuzzy import process  # Import for fuzzy matching
from main import create_embed

# Dictionary of descriptions for the AM functionality
am_descriptions = {
    "Opslag rush": """Placeholder text for Opslag rush.
    
    📁 - **TEMPLATE**
    Placeholder voor template
    """,
    "ZC rush": """Placeholder text for ZC rush.
    
    📁 - **TEMPLATE**
    Placeholder voor template
    """,
    "AH rush": """Bouw een adelshoeve in 8 dagen zonder PP inzet.
    
    📁 - **TEMPLATE**
    Placeholder voor template
    """,
    "Muur rush": """Placeholder text for Muur rush.
    
    📁 - **TEMPLATE**
    Placeholder voor template
    """,
    "Toren rush": """Placeholder text for Toren rush.
    
    📁 - **TEMPLATE**
    Placeholder voor template
    """,
    "Kerk rush": """Placeholder text for Kerk rush.
    
    📁 - **TEMPLATE**
    Placeholder voor template
    """,
    "Muur spoed": """Placeholder text for Muur spoed.
    
    📁 - **TEMPLATE**
    Placeholder voor template
    """,
    "OFF sjabloon": """Placeholder text for OFF sjabloon.
    
    📁 - **TEMPLATE**
    Placeholder voor template
    """,
    "DEF sjabloon": """Placeholder text for DEF sjabloon.
    
    📁 - **TEMPLATE**
    Placeholder voor template
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
    @app_commands.command(name="am", description="Displays the AM options menu.")
    async def am(self, interaction: Interaction):
        embed = create_embed("AM sjablonen", "Selecteer welk sjabloon je wilt bekijken")
        await interaction.response.send_message(embed=embed, view=AMView(self.bot), ephemeral=True)

    # Text command for !am <template_name> for direct template lookup
    @commands.command(name="am_template", help="Finds a specific AM template by name.")
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
