import discord
from discord.ext import commands
from discord import Interaction
from discord.ui import View, Button, Modal, Select
from scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

# Helper function to combine script codes from selected scripts
def get_combined_script_code(selected_scripts):
    combined_code = "javascript:\n"
    for script_name in selected_scripts:
        description = descriptions.get(script_name, "")
        script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript")]
        combined_code += "\n".join(script_lines) + "\n"
    return combined_code.strip()

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to open the modal for combining scripts
    @commands.command(name="group_scripts", help="Combine scripts into a single script for faster loading.")
    async def group_scripts(self, ctx):
        await ctx.send("Selecteer scripts om te combineren:", view=ScriptCombineView(self.bot))

# Modal for grouping scripts
class ScriptCombineModal(Modal):
    def __init__(self, bot, selected_scripts):
        super().__init__(title="Gecombineerde Script Code")
        self.bot = bot
        self.selected_scripts = selected_scripts

    async def on_submit(self, interaction: Interaction):
        combined_code = get_combined_script_code(self.selected_scripts)
        embed = create_embed(
            title="Gecombineerde scriptcode",
            description=f"```js\n{combined_code}\n```"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# Selection view for combining scripts
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

        # Add "Combine" button to confirm selection and show combined code
        combine_button = Button(label="Combineer Geselecteerde Scripts", style=discord.ButtonStyle.success)
        combine_button.callback = self.show_combine_modal
        self.add_item(combine_button)

    async def select_scripts(self, interaction: Interaction):
        self.selected_scripts = self.select.values

    async def show_combine_modal(self, interaction: Interaction):
        if not self.selected_scripts:
            await interaction.response.send_message("Geen scripts geselecteerd. Selecteer ten minste één script.", ephemeral=True)
        else:
            await interaction.response.send_modal(ScriptCombineModal(self.bot, self.selected_scripts))


async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
