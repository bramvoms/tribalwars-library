import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Modal, Select
from cogs.scripts_cog import descriptions
from main import create_embed
import requests

# Your Pastebin API Key (Replace this with your actual key)
PASTEBIN_API_KEY = 'IIqOr2TN7b7dp9pS1O34-b8oFmlyJ8mI'

# Helper function to combine selected scripts into one combined code
def get_combined_script_code(selected_scripts):
    combined_code = "javascript:\n"
    for script_name in selected_scripts:
        description = descriptions.get(script_name)
        if description:
            script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript")]
            combined_code += "\n".join(script_lines) + "\n"
    return combined_code.strip()

# Function to upload combined code to Pastebin and return the URL
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
        await interaction.response.defer(ephemeral=True)
        try:
            # Send the script selection view after deferring the response
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

        # Combine the selected scripts into one
        combined_code = get_combined_script_code(self.selected_scripts)

        # Show two buttons to either send the code to DM or upload to Pastebin
        confirmation_view = ConfirmationView(self.bot, combined_code)
        await interaction.followup.send("Kies een optie om de gecombineerde scriptcode te verzenden.", view=confirmation_view)

class ConfirmationView(View):
    def __init__(self, bot, combined_code):
        super().__init__(timeout=None)
        self.bot = bot
        self.combined_code = combined_code

        # Button to send the combined code to the user's DM
        send_dm_button = Button(label="Stuur naar DM", style=discord.ButtonStyle.primary)
        send_dm_button.callback = self.send_to_dm
        self.add_item(send_dm_button)

        # Button to upload to Pastebin and send the link in DM
        upload_pastebin_button = Button(label="Upload naar Pastebin en stuur naar DM", style=discord.ButtonStyle.success)
        upload_pastebin_button.callback = self.upload_to_pastebin_and_send
        self.add_item(upload_pastebin_button)

    async def send_to_dm(self, interaction: discord.Interaction):
        try:
            user_dm = await interaction.user.create_dm()
            await user_dm.send(f"Gecombineerde scriptcode:\n```js\n{self.combined_code}\n```")
            await interaction.response.send_message("De gecombineerde scriptcode is verzonden naar je DM.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Er is iets misgegaan bij het sturen van de scriptcode naar je DM: {e}", ephemeral=True)

    async def upload_to_pastebin_and_send(self, interaction: discord.Interaction):
        paste_url = upload_to_pastebin(self.combined_code)
        if paste_url:
            try:
                user_dm = await interaction.user.create_dm()
                await user_dm.send(f"Gecombineerde scriptcode is opgeslagen op Pastebin: {paste_url}")
                await interaction.response.send_message("De Pastebin link is verzonden naar je DM.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Er is iets misgegaan bij het sturen van de Pastebin-link naar je DM: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
