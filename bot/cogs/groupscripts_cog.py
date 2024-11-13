import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Modal, Select
from cogs.scripts_cog import descriptions  # Import descriptions from cogs.scripts_cog
from main import create_embed

# Helper function to combine script codes from selected scripts
def get_combined_script_code(selected_scripts):
    print("Combining script codes")  # Debug print
    combined_code = "javascript:\n"
    for script_name in selected_scripts:
        description = descriptions.get(script_name, "")
        script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript")]
        combined_code += "\n".join(script_lines) + "\n"
        print(f"Added script for {script_name}")  # Debug print
    return combined_code.strip()

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Initialized GroupScriptsCog")  # Debug print

# Slash command to open the modal for combining scripts
@app_commands.command(name="group_scripts", description="Combine scripts into a single script for faster loading.")
async def group_scripts(self, interaction):  # Removed type hint
    print("Received /group_scripts command")  # Debug print
    
    # Acknowledge the interaction immediately to prevent timeout
    try:
        await interaction.response.defer(ephemeral=True)
        print("Interaction deferred successfully")  # Debug print
    except Exception as e:
        print(f"Error deferring interaction: {e}")  # Debug print
    
    # Send the selection view after deferring the response
    try:
        await interaction.followup.send("Selecteer scripts om te combineren:", view=ScriptCombineView(self.bot))
        print("Sent ScriptCombineView to user")  # Debug print
    except Exception as e:
        print(f"Error sending followup message: {e}")  # Debug print

# Modal for displaying combined scripts
class ScriptCombineModal(Modal):
    def __init__(self, bot, selected_scripts):
        super().__init__(title="Gecombineerde Script Code")
        self.bot = bot
        self.selected_scripts = selected_scripts
        print("Initialized ScriptCombineModal")  # Debug print

    async def on_submit(self, interaction: "Interaction"):
        print("Submitting combined script modal")  # Debug print
        combined_code = get_combined_script_code(self.selected_scripts)
        embed = create_embed(
            title="Gecombineerde scriptcode",
            description=f"```js\n{combined_code}\n```"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print("Sent combined script code to user")  # Debug print

# Selection view for combining scripts
class ScriptCombineView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.selected_scripts = []

        print("Initialized ScriptCombineView")  # Debug print

        # Dropdown selection for multiple scripts
        options = [discord.SelectOption(label=script) for script in descriptions.keys()]
        self.select = Select(placeholder="Select scripts to combine", options=options, min_values=1, max_values=len(options))
        self.select.callback = self.select_scripts
        self.add_item(self.select)
        print("Added script selection dropdown")  # Debug print

        # Add "Combine" button to confirm selection and show combined code
        combine_button = Button(label="Combineer Geselecteerde Scripts", style=discord.ButtonStyle.success)
        combine_button.callback = self.show_combine_modal
        self.add_item(combine_button)
        print("Added Combine Scripts button")  # Debug print

    async def select_scripts(self, interaction: "Interaction"):
        self.selected_scripts = self.select.values
        print(f"Selected scripts: {self.selected_scripts}")  # Debug print
        await interaction.response.defer()

    async def show_combine_modal(self, interaction: "Interaction"):
        if not self.selected_scripts:
            print("No scripts selected")  # Debug print
            await interaction.response.send_message("Geen scripts geselecteerd. Selecteer ten minste één script.", ephemeral=True)
        else:
            print("Opening ScriptCombineModal")  # Debug print
            await interaction.response.send_modal(ScriptCombineModal(self.bot, self.selected_scripts))

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
    print("Loaded GroupScriptsCog")  # Debug print
