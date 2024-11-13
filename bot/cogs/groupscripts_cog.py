import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Modal, Select
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

# Helper function to combine script codes from selected scripts
def get_combined_script_code(selected_scripts):
    combined_code = "javascript:\n"
    for script_name in selected_scripts:
        description = descriptions.get(script_name, "")
        script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript")]
        combined_code += "\n".join(script_lines) + "\n"
    print(f"Combined script code:\n{combined_code.strip()}")  # Debug print
    return combined_code.strip()

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command to open the modal for combining scripts
    @app_commands.command(name="group_scripts", description="Combine scripts into a single script for faster loading.")
    async def group_scripts(self, interaction: discord.Interaction):
        print("Received /group_scripts command")  # Debug print
        await interaction.response.defer(ephemeral=True)
        print("Interaction deferred successfully")  # Debug print
        
        # Send the selection view after deferring the response
        try:
            await interaction.followup.send("Selecteer scripts om te combineren:", view=ScriptCombineView(self.bot))
            print("Sent ScriptCombineView to user")  # Debug print
        except Exception as e:
            print(f"Error sending ScriptCombineView: {e}")  # Print any errors encountered

class ScriptCombineModal(Modal):
    def __init__(self, bot, selected_scripts):
        super().__init__(title="Gecombineerde Script Code")
        self.bot = bot
        self.selected_scripts = selected_scripts

    async def on_submit(self, interaction: discord.Interaction):
        combined_code = get_combined_script_code(self.selected_scripts)
        embed = create_embed(
            title="Gecombineerde scriptcode",
            description=f"```js\n{combined_code}\n```"
        )
        print("Sending combined script code embed")  # Debug print
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ScriptCombineView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.selected_scripts = []
        print("Initialized ScriptCombineView")  # Debug print

        # Divide options into chunks of 25 or less
        option_chunks = [list(descriptions.keys())[i:i+25] for i in range(0, len(descriptions), 25)]
        
        # Create a dropdown for each chunk of options
        for i, chunk in enumerate(option_chunks, start=1):
            options = [discord.SelectOption(label=script) for script in chunk]
            select = Select(placeholder=f"Select scripts (set {i})", options=options, min_values=1, max_values=len(options))
            select.callback = self.select_scripts
            self.add_item(select)
            print(f"Added script selection dropdown for chunk {i}")  # Debug print

        # Add "Combine" button to confirm selection and show combined code
        combine_button = Button(label="Combineer Geselecteerde Scripts", style=discord.ButtonStyle.success)
        combine_button.callback = self.show_combine_modal
        self.add_item(combine_button)
        print("Added Combine Scripts button")  # Debug print

    async def select_scripts(self, interaction: discord.Interaction):
        # Add selected scripts from the dropdown to self.selected_scripts
        self.selected_scripts.extend(self.select.values)
        print(f"Selected scripts: {self.selected_scripts}")  # Debug print to confirm selection
        await interaction.response.defer()  # Defer the response to avoid "interaction failed" error

    async def show_combine_modal(self, interaction: discord.Interaction):
        print("Combine button clicked")  # Debug print
        if not self.selected_scripts:
            await interaction.response.send_message("Geen scripts geselecteerd. Selecteer ten minste één script.", ephemeral=True)
            print("No scripts selected message sent")  # Debug print
        else:
            print(f"Opening combine modal with selected scripts: {self.selected_scripts}")  # Debug print
            try:
                await interaction.response.send_modal(ScriptCombineModal(self.bot, self.selected_scripts))
            except Exception as e:
                print(f"Error opening combine modal: {e}")  # Capture any issues with the modal

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
