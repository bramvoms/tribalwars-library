import discord
from discord.ext import commands
from discord import Interaction
from discord.ui import View, Button, Modal, Checkbox
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
    def __init__(self, bot):
        super().__init__(title="Combineer scripts")
        self.bot = bot
        self.selected_scripts = []

        # Create a checkbox for each script in descriptions
        for script_name in descriptions.keys():
            checkbox = Checkbox(label=script_name)
            checkbox.callback = lambda interaction, name=script_name: self.toggle_selection(name)
            self.add_item(checkbox)

    def toggle_selection(self, script_name):
        if script_name in self.selected_scripts:
            self.selected_scripts.remove(script_name)
        else:
            self.selected_scripts.append(script_name)

    async def on_submit(self, interaction: Interaction):
        combined_code = get_combined_script_code(self.selected_scripts)
        embed = create_embed(
            title="Gecombineerde scriptcode",
            description=f"```js\n{combined_code}\n```"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# Checkbox selection view for combining scripts
class ScriptCombineView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

        # Add "Combine" button to open modal
        combine_button = Button(label="Combineer Geselecteerde Scripts", style=discord.ButtonStyle.success)
        combine_button.callback = self.show_combine_modal
        self.add_item(combine_button)

    async def show_combine_modal(self, interaction: Interaction):
        await interaction.response.send_modal(ScriptCombineModal(self.bot))


async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
