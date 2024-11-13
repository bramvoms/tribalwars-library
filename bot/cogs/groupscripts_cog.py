import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Select
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="group_scripts", description="Combine scripts into a single script for faster loading.")
    async def group_scripts(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)  # Defer to prevent timeout
        try:
            # Send the script selection view after deferring
            await interaction.followup.send("Selecteer scripts om te combineren:", view=ScriptCombineView(self.bot))
        except Exception as e:
            print(f"Error sending script selection view: {e}")

class ScriptCombineView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.selected_scripts = []
        
        # Divide the script options into chunks of 25 or less
        options_chunks = [list(descriptions.keys())[i:i + 25] for i in range(0, len(descriptions), 25)]
        for i, chunk in enumerate(options_chunks, start=1):
            options = [discord.SelectOption(label=script) for script in chunk]
            select = Select(placeholder=f"Select scripts (part {i})", options=options, min_values=1, max_values=len(options))
            select.callback = self.select_scripts
            self.add_item(select)

        # Add "Combine" button to confirm selection and show combined code
        combine_button = Button(label="Combineer Geselecteerde Scripts", style=discord.ButtonStyle.success)
        combine_button.callback = self.show_combined_code
        self.add_item(combine_button)

    async def select_scripts(self, interaction: discord.Interaction):
        selected_values = interaction.data["values"]
        self.selected_scripts.extend(selected_values)
        self.selected_scripts = list(set(self.selected_scripts))  # Remove duplicates
        await interaction.response.defer()  # Defer response to avoid timeout

    async def show_combined_code(self, interaction: discord.Interaction):
        if not self.selected_scripts:
            await interaction.followup.send("Geen scripts geselecteerd. Selecteer ten minste één script.", ephemeral=True)
            return

        combined_code = self.get_combined_script_code(self.selected_scripts)

        # Send the combined code directly to the user's DM
        try:
            user_dm = await interaction.user.create_dm()  # Ensure the user has a DM channel open
            await user_dm.send(f"Gecombineerde scriptcode:\n```js\n{combined_code}\n```")
            
            # Send confirmation in the channel that the DM has been sent
            await interaction.followup.send("De gecombineerde scriptcode is verzonden naar je DM.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Er is iets misgegaan bij het sturen van de gecombineerde scriptcode naar je DM: {e}", ephemeral=True)

    def get_combined_script_code(self, selected_scripts):
        combined_code = "javascript:\n"
        for script_name in selected_scripts:
            description = descriptions.get(script_name)
            if description:
                script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript")]
                combined_code += "\n".join(script_lines) + "\n"
        return combined_code.strip()

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
