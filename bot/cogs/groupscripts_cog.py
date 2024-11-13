import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Select
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="group_scripts", description="Combine scripts into a single script for faster loading.")
    async def group_scripts(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        view = ScriptCombineView()
        embed = create_embed("Select Scripts to Combine", "Select scripts to add or remove them from the combined code.")
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)  # Make this private

class ScriptCombineView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.selected_scripts = set()  # Track selected scripts to manage adding/removing

        # Divide scripts into chunks of 20 for multiple selection menus
        script_chunks = [list(descriptions.keys())[i:i + 20] for i in range(0, len(descriptions), 20)]
        
        # Create a Select menu for each chunk
        for i, chunk in enumerate(script_chunks, start=1):
            options = [discord.SelectOption(label=script, value=script) for script in chunk]
            select = Select(placeholder=f"Select scripts (Group {i})", options=options, min_values=1, max_values=len(options))
            select.callback = self.update_combined_code
            self.add_item(select)

    async def update_combined_code(self, interaction: discord.Interaction):
        selected_values = set(interaction.data["values"])
        
        # Update selected scripts, adding or removing as necessary
        self.selected_scripts.symmetric_difference_update(selected_values)  # Toggle each script in/out of selection

        # Build the combined script code
        combined_code = "javascript:\n"
        for script in self.selected_scripts:
            description = descriptions.get(script)
            if description:
                combined_code += self.extract_script_lines(description)

        # Update options to keep selected items highlighted
        for select in self.children:
            if isinstance(select, Select):
                for option in select.options:
                    option.default = option.value in self.selected_scripts

        # Update message with the current combined code
        embed = create_embed("Combined Script Code", f"```js\n{combined_code}\n```")
        await interaction.response.edit_message(embed=embed, view=self, ephemeral=True)  # Make this private

    def extract_script_lines(self, description):
        lines = ""
        for line in description.splitlines():
            if line.strip().startswith("$.getScript") or "var" in line:
                lines += line.strip() + "\n"
        return lines

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
