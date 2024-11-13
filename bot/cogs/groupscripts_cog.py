import discord
import requests  # This will let us make requests to Pastebin
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Select
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed
import logging

# Set up logging to capture everything
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
            logger.debug(f"Added {script_name} to combined code.")
        else:
            logger.warning(f"No description found for {script_name}: Skipping.")
    logger.debug(f"Combined code:\n{combined_code}")
    return combined_code.strip()

# Function to upload the combined code to Pastebin and return the URL
def upload_to_pastebin(code):
    logger.debug("Uploading combined code to Pastebin...")
    url = "https://pastebin.com/api/api_post.php"
    data = {
        'api_dev_key': PASTEBIN_API_KEY,
        'api_option': 'paste',
        'api_paste_code': code,
        'api_paste_private': 1,  # 1 = unlisted, 0 = public
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        logger.info(f"Pastebin URL created: {response.text}")
        return response.text
    else:
        logger.error(f"Failed to create Pastebin paste: {response.text}")
        return None

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.debug("GroupScriptsCog initialized.")

    @app_commands.command(name="group_scripts", description="Combine scripts into a single script for faster loading.")
    async def group_scripts(self, interaction: discord.Interaction):
        logger.debug("Received /group_scripts command.")
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.followup.send("Selecteer scripts om te combineren:", view=ScriptCombineView(self.bot))
            logger.debug("Sent ScriptCombineView to user.")
        except Exception as e:
            logger.error(f"Error sending script selection view: {e}")

class ScriptCombineView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.selected_scripts = []
        logger.debug("Initialized ScriptCombineView")

        options_chunks = [list(descriptions.keys())[i:i + 25] for i in range(0, len(descriptions), 25)]
        for i, chunk in enumerate(options_chunks, start=1):
            options = [discord.SelectOption(label=script) for script in chunk]
            select = Select(placeholder=f"Select scripts (part {i})", options=options, min_values=1, max_values=len(options))
            select.callback = self.select_scripts
            self.add_item(select)
            logger.debug(f"Added script selection dropdown for chunk {i}")

        combine_button = Button(label="Combineer Geselecteerde Scripts", style=discord.ButtonStyle.success)
        combine_button.callback = self.show_combined_code
        self.add_item(combine_button)
        logger.debug("Added Combine Scripts button")

    async def select_scripts(self, interaction: discord.Interaction):
        selected_values = interaction.data["values"]
        self.selected_scripts.extend(selected_values)
        self.selected_scripts = list(set(self.selected_scripts))
        logger.debug(f"Current selected scripts: {self.selected_scripts}")
        await interaction.response.defer()

    async def show_combined_code(self, interaction: discord.Interaction):
        logger.debug("Combine button clicked.")
        if not self.selected_scripts:
            await interaction.followup.send("Geen scripts geselecteerd. Selecteer ten minste één script.", ephemeral=True)
            logger.warning("No scripts selected.")
            return

        logger.debug(f"Combining selected scripts: {self.selected_scripts}")
        combined_code = get_combined_script_code(self.selected_scripts)
        paste_url = upload_to_pastebin(combined_code)

        if paste_url:
            logger.debug(f"Sending Pastebin URL to user: {paste_url}")
            try:
                await interaction.user.send(f"Gecombineerde scriptcode is opgeslagen op Pastebin: {paste_url}")
                logger.debug("Successfully sent Pastebin URL to user via DM.")
            except Exception as e:
                logger.error(f"Error sending Pastebin URL to user via DM: {e}")
        else:
            await interaction.followup.send("Er is iets misgegaan bij het maken van de Pastebin-link.", ephemeral=True)
            logger.error("Failed to upload combined code to Pastebin.")

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
    logger.debug("GroupScriptsCog added to bot.")

