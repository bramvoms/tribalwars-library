import discord
import requests  # This will let us make requests to Pastebin
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Select
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

# Your Pastebin API Key
PASTEBIN_API_KEY = 'IIqOr2TN7b7dp9pS1O34-b8oFmlyJ8mI'  # Replace with your Pastebin API key

# Helper function to combine script codes and send to Pastebin
def get_combined_script_code(selected_scripts):
    combined_code = "javascript:\n"
    for script_name in selected_scripts:
        description = descriptions.get(script_name)
        if description:
            script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript")]
            combined_code += "\n".join(script_lines) + "\n"
    return combined_code.strip()

# Function to upload the combined code to Pastebin and return the URL
def upload_to_pastebin(code):
    url = "https://pastebin.com/api/api_post.php"
    data = {
        'api_dev_key': PASTEBIN_API_KEY,
        'api_option': 'paste',
        'api_paste_code': code,
        'api_paste_private': 1,  # 1 = unlisted, 0 = public
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.text
    else:
        return None

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="group_scripts", description="Combine scripts into a single script for faster loading.")
    async def group_scripts(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)  # Defer to prevent timeout
        try:
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
        self.selected_scripts = list(set(self.selected_scripts))
        await interaction.response.defer()

    async def show_combined_code(self, interaction: discord.Interaction):
        if not self.selected_scripts:
            await interaction.followup.send("Geen scripts geselecteerd. Selecteer ten minste één script.", ephemeral=True)
            return

        combined_code = get_combined_script_code(self.selected_scripts)
        paste_url = upload_to_pastebin(combined_code)

        if paste_url:
            try:
                await interaction.user.send(f"Gecombineerde scriptcode is opgeslagen op Pastebin: {paste_url}")
                await interaction.followup.send("De gecombineerde scriptcode is verzonden naar je DM.", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"Er is iets misgegaan bij het sturen van de link naar je DM: {e}", ephemeral=True)
        else:
            await interaction.followup.send("Er is iets misgegaan bij het maken van de Pastebin-link.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
