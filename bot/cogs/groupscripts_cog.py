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
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.followup.send("Click the dropdowns to select scripts:", view=ScriptCombineView(self.bot, interaction.user))
        except Exception as e:
            print(f"Error sending script selection view: {e}")

class ScriptCombineView(View):
    def __init__(self, bot, user):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.selected_scripts = set()  # Store selected scripts to avoid duplicates

        # Divide script options into chunks of 20
        options_chunks = [list(descriptions.keys())[i:i + 20] for i in range(0, len(descriptions), 20)]
        
        # Create a Select menu for each chunk of options
        for i, chunk in enumerate(options_chunks, start=1):
            options = [discord.SelectOption(label=script, value=script) for script in chunk]
            select = Select(placeholder=f"Select scripts (group {i})", options=options, min_values=1, max_values=len(options))
            select.callback = self.select_scripts
            self.add_item(select)

        # Add "Combine" button to confirm selection and show combined code
        combine_button = Button(label="Combine Selected Scripts", style=discord.ButtonStyle.success)
        combine_button.callback = self.show_combined_code
        self.add_item(combine_button)

    async def select_scripts(self, interaction: discord.Interaction):
        # Collect selected scripts from the dropdown
        selected_values = interaction.data["values"]
        self.selected_scripts.update(selected_values)  # Update selected scripts, avoiding duplicates
        await interaction.response.defer()  # Defer response to avoid timeout

    async def show_combined_code(self, interaction: discord.Interaction):
        if not self.selected_scripts:
            await interaction.followup.send("No scripts selected. Select at least one script.", ephemeral=True)
            return

        # Combine the selected scripts into one
        combined_code = self.get_combined_script_code(self.selected_scripts)

        # Send the combined code directly to the user's DM
        try:
            user_dm = await interaction.user.create_dm()  # Ensure the user has a DM channel open
            await user_dm.send(f"Combined script code:\n```js\n{combined_code}\n```")
            await interaction.followup.send("The combined script code has been sent to your DM.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"There was an issue sending the combined script code to your DM: {e}", ephemeral=True)

    def get_combined_script_code(self, selected_scripts):
        combined_code = "javascript:\n"
        for script_name in selected_scripts:
            description = descriptions.get(script_name)
            if description:
                # Extract $.getScript and variables from the description
                for line in description.splitlines():
                    combined_code += line.strip() + "\n" if line.strip().startswith("$.getScript") else line.strip() + "\n"
        return combined_code.strip()

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
