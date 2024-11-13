import discord
from discord.ext import commands
from discord import app_commands, Interaction
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

# Modal for grouping scripts with a limit of 5 scripts per modal
class ScriptCombineModal(Modal):
    def __init__(self, bot, selected_scripts):
        super().__init__(title="Gecombineerde Script Code")
        self.bot = bot
        self.selected_scripts = selected_scripts

    async def on_submit(self, interaction: Interaction):
        combined_code = get_combined_script_code(self.selected_scripts)
        
        # Split the message if it exceeds Discord's limits
        code_chunks = [combined_code[i:i+2000] for i in range(0, len(combined_code), 2000)]
        
        for chunk in code_chunks:
            embed = create_embed(
                title="Gecombineerde scriptcode",
                description=f"```js\n{chunk}\n```"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

class ScriptCombineView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.selected_scripts = []

        # Dropdown selection for multiple scripts
        options = [discord.SelectOption(label=script) for script in descriptions.keys()]
        self.select = Select(placeholder="Select scripts to combine", options=options, min_values=1, max_values=len(options))
        self.select.callback = self.select_scripts
        self.add_item(self.select)

        # Add "Combine" button to confirm selection and send combined code
        combine_button = Button(label="Combineer Geselecteerde Scripts", style=discord.ButtonStyle.success)
        combine_button.callback = self.send_combined_code  # Send the combined code directly
        self.add_item(combine_button)

    async def select_scripts(self, interaction: Interaction):
        self.selected_scripts = self.select.values
        print(f"Current selected scripts: {self.selected_scripts}")

    async def send_combined_code(self, interaction: Interaction):
        if not self.selected_scripts:
            await interaction.response.send_message("Geen scripts geselecteerd. Selecteer ten minste één script.", ephemeral=True)
        else:
            print("Combine button clicked")
            combined_code = get_combined_script_code(self.selected_scripts)
            
            # Split the combined code if it’s too long for a single embed
            code_chunks = [combined_code[i:i+2000] for i in range(0, len(combined_code), 2000)]
            
            for chunk in code_chunks:
                embed = create_embed(
                    title="Gecombineerde scriptcode",
                    description=f"```js\n{chunk}\n```"
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
