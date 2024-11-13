import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="group_scripts", description="Combine scripts into a single script for faster loading.")
    async def group_scripts(self, interaction: discord.Interaction):
        # Acknowledge the interaction immediately to prevent timeout
        await interaction.response.defer(ephemeral=True)
        
        # Create and send the script selection view
        try:
            await interaction.followup.send("Click the buttons to add scripts:", view=ScriptCombineView(self.bot, interaction.user))
        except Exception as e:
            print(f"Error sending script selection view: {e}")

class ScriptCombineView(View):
    def __init__(self, bot, user):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.selected_scripts = set()  # Store selected scripts in a set to avoid duplicates
        self.message_content = ""  # To store the message content dynamically

        # Add buttons for each script
        for script_name in descriptions.keys():
            button = Button(label=script_name, style=discord.ButtonStyle.primary)
            button.callback = self.toggle_script
            self.add_item(button)

    async def toggle_script(self, interaction: discord.Interaction):
        script_name = interaction.data["custom_id"]
        
        if script_name in self.selected_scripts:
            # Remove the script from the selection
            self.selected_scripts.remove(script_name)
            self.message_content = self.message_content.replace(self.get_script_code(script_name), "")
        else:
            # Add the script to the selection
            self.selected_scripts.add(script_name)
            self.message_content += self.get_script_code(script_name) + "\n"
        
        # Update the message with the current combined script
        await interaction.response.edit_message(content=self.message_content or "Click the buttons to add scripts:", view=self)

    def get_script_code(self, script_name):
        """Helper function to return the code for a script (getScript line + variables)."""
        description = descriptions.get(script_name, "")
        script_code = ""
        
        # Extract the $.getScript line
        for line in description.splitlines():
            if line.strip().startswith("$.getScript"):
                script_code += line.strip() + "\n"
        
        # Extract variables and add them to the script
        for line in description.splitlines():
            if not line.strip().startswith("$.getScript"):
                script_code += line.strip() + "\n"
        
        return script_code.strip()

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
