import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button
from fuzzywuzzy import process  # Import for fuzzy matching
import deepl
from main import create_embed

# Initialize DeepL Translator with your API key
DEEPL_AUTH_KEY = "f58d2e0f-d065-4d78-bc69-19e728f1ca61:fx"  # Replace with your actual API key
translator = deepl.Translator(auth_key=DEEPL_AUTH_KEY)

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

class AMCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="amtemplates", description="Displays the AM templates menu")
    async def amtemplates(self, interaction: Interaction):
        """Slash command to display the AM templates menu."""
        title = "⚙️ ** AM TEMPLATES ** ⚙️"
        embed = create_embed(
            title=title,
            description="Select which template you want to view.\nCopy the text under TEMPLATE and paste it ingame:\nAccount Manager > Construction > Manage templates > Import template."
        )
        await interaction.response.send_message(embed=embed, view=AMView(self.bot), ephemeral=True)

    @commands.command(name="amtemplates", help="Find a specific AM template")
    async def amtemplates_text(self, ctx, *, template_name: str):
        """Text command implementation for &amtemplates <template_name>."""
        try:
            if not template_name.strip():
                raise ValueError("Template name cannot be empty.")

            # Translate the input to English
            translation_result = translator.translate_text(template_name.strip(), target_lang="EN-US")
            translated_name = translation_result.text.lower().strip()

            # Combined dataset for fuzzy matching
            combined_data = {
                title: f"{title.lower()} {description.lower()}" for title, description in am_descriptions.items()
            }

            # Perform fuzzy matching
            matches = process.extract(translated_name, combined_data.values(), limit=5)
            top_matches = [
                (title, combined_data[title])
                for title, full_text in combined_data.items()
                for match in matches
                if full_text == match[0] and match[1] > 60
            ]

            if not top_matches:
                embed = create_embed("Template Not Found", f"No template found matching '{template_name}'.")
                await ctx.send(embed=embed)
                return

            if len(top_matches) == 1:
                template, _ = top_matches[0]
                description = am_descriptions[template]
                title = f"━ {template.upper()} ━"
                embed = create_embed(title=title, description=description)
                await ctx.send(embed=embed)
            else:
                view = TemplateSelectionView(ctx, [match[0] for match in top_matches], am_descriptions)
                await ctx.send("Multiple templates found. Please select one:", view=view)
        except ValueError as ve:
            await ctx.send(f"Invalid input: {ve}")
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}")


class AMView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        for label in am_descriptions.keys():
            button = Button(label=label, style=discord.ButtonStyle.primary)
            button.callback = lambda interaction, label=label: self.show_am_description(interaction, label)
            self.add_item(button)

    async def show_am_description(self, interaction: Interaction, subcategory):
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
        title = "⚙️ ** AM TEMPLATES ** ⚙️"
        embed = create_embed(
            title=title,
            description="Select which template you want to view.\nCopy the text under TEMPLATE and paste it ingame:\nAccount Manager > Construction > Manage templates > Import template."
        )
        await interaction.response.edit_message(embed=embed, view=self)


class TemplateSelectionView(discord.ui.View):
    def __init__(self, ctx, templates, descriptions):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.templates = templates
        self.descriptions = descriptions

        for template in templates:
            button = discord.ui.Button(label=template, style=discord.ButtonStyle.primary)
            button.callback = self.make_callback(template)
            self.add_item(button)

    def make_callback(self, template):
        async def callback(interaction: Interaction):
            description = self.descriptions[template]
            title = f"━ {template.upper()} ━"
            embed = create_embed(title=title, description=description)
            await interaction.response.edit_message(content=None, embed=embed, view=None)
        return callback
        
async def setup(bot):
    await bot.add_cog(AMCog(bot))

        
