import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

# Helper function to combine script codes from selected scripts
def get_combined_script_code(selected_scripts):
    combined_code = "javascript:\n"
    for script_name in selected_scripts:
        description = descriptions.get(script_name)
        if description:
            # Extract lines that contain $.getScript
            script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript")]
            combined_code += "\n".join(script_lines) + "\n"
            print(f"Added {script_name} to combined code.")
        else:
            print(f"{script_name} missing description.")

    return combined_code.strip()

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command to open the modal for combining scripts
    @app_commands.command(name="group_scripts", description="Combine scripts into a single script for faster loading.")
    async def group_scripts(self, interaction: discord.Interaction):
        print("Group scripts command triggered.")
        await interaction.response.defer(ephemeral=True)

        # Send the view for script selection
        try:
            await interaction.followup.send("Selecteer scripts om te combineren:", view=ScriptCombineView(self.bot))
            print("Script selection view sent to user.")
        except Exception as e:
            print(f"Error sending script selection view: {e}")

class ScriptCombineView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.selected_scripts = []
        print("Initialized ScriptCombineView")

        # Divide descriptions into chunks of 25 or less
        options_chunks = [list(descriptions.keys())[i:i + 25] for i in range(0, len(descriptions), 25)]
        
        # Create a dropdown for each chunk of options
        for i, chunk in enumerate(options_chunks, start=1):
            options = [discord.SelectOption(label=script) for script in chunk]
            select = Select(placeholder=f"Select scripts (part {i})", options=options, min_values=1, max_values=len(options))
            select.callback = self.select_scripts
            self.add_item(select)
            print(f"Added script selection dropdown for chunk {i}")

        # Combine button to finalize selection and show combined code
        combine_button = Button(label="Combineer Geselecteerde Scripts", style=discord.ButtonStyle.success)
        combine_button.callback = self.show_combined_code
        self.add_item(combine_button)
        print("Combine Scripts button added")

    async def select_scripts(self, interaction: discord.Interaction):
        # Append selected scripts from dropdown
        selected_values = interaction.data["values"]
        self.selected_scripts.extend(selected_values)

        # Remove duplicates
        self.selected_scripts = list(set(self.selected_scripts))
        print(f"Current selected scripts: {self.selected_scripts}")

        # Acknowledge the interaction with a deferred response to avoid "interaction failed"
        await interaction.response.defer()

    async def show_combined_code(self, interaction: discord.Interaction):
        print("Combine button clicked")
        if not self.selected_scripts:
            await interaction.response.send_message("Geen scripts geselecteerd. Selecteer ten minste één script.", ephemeral=True)
            print("No scripts selected message sent")
            return

        combined_code = get_combined_script_code(self.selected_scripts)
        if not combined_code:
            await interaction.followup.send("Geen geldige scripts gevonden om te combineren.", ephemeral=True)
            print("No valid script lines found.")
            return

        # Send the combined code back to the user
        try:
            await interaction.followup.send(f"Gecombineerde scriptcode:\n```js\n{combined_code}\n```", ephemeral=True)
            print("Combined code sent to user.")
        except Exception as e:
            print(f"Error sending combined code: {e}")

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
