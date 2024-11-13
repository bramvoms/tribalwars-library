import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Select, Button
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="group_scripts", description="Combine scripts into a single script for faster loading.")
    async def group_scripts(self, interaction: discord.Interaction):
        await interaction.response.defer()
        view = ScriptCombineView()
        embed = create_embed("Select Scripts to Combine", "Select scripts and click 'Combine Now' to receive the combined code in your DMs.")
        await interaction.followup.send(embed=embed, view=view)

class ScriptCombineView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.selected_scripts = set()

        # Divide the script options into chunks of 20 for selection menus
        script_chunks = [list(descriptions.keys())[i:i + 20] for i in range(0, len(descriptions), 20)]
        
        for i, chunk in enumerate(script_chunks, start=1):
            options = [discord.SelectOption(label=script, value=script) for script in chunk]
            select = Select(placeholder=f"Select scripts (Group {i})", options=options, min_values=0, max_values=len(options))
            select.callback = self.update_selected_scripts
            self.add_item(select)

        combine_button = Button(label="Combine Now", style=discord.ButtonStyle.success)
        combine_button.callback = self.send_combined_code
        self.add_item(combine_button)

    async def update_selected_scripts(self, interaction: discord.Interaction):
        selected_values = set(interaction.data["values"])
        self.selected_scripts.symmetric_difference_update(selected_values)

        for select in self.children:
            if isinstance(select, Select):
                for option in select.options:
                    option.default = option.value in self.selected_scripts

        await interaction.response.defer()

    async def send_combined_code(self, interaction: discord.Interaction):
        if not self.selected_scripts:
            await interaction.followup.send("No scripts selected. Please select at least one script.", ephemeral=True)
            return

        combined_code = self.get_combined_script_code()

        try:
            user_dm = await interaction.user.create_dm()
            await user_dm.send(f"Here is your combined script code:\n```js\n{combined_code}\n```")
            await interaction.followup.send("The combined script code has been sent to your DMs.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error sending DM: {e}", ephemeral=True)

    def get_combined_script_code(self):
        combined_code = "javascript:\n"
        variable_blocks = []
        script_lines = []

        for script_name in self.selected_scripts:
            description = descriptions.get(script_name)
            if description:
                current_vars = []
                current_scripts = []
                
                for line in description.splitlines():
                    line = line.strip()
                    if line.startswith("$.getScript"):
                        current_scripts.append(line)
                    elif "var" in line or line.endswith("{") or line.endswith("};"):
                        current_vars.append(line)

                if current_vars:
                    variable_blocks.append("\n".join(current_vars))
                if current_scripts:
                    script_lines.extend(current_scripts)

        combined_code += "\n".join(variable_blocks) + "\n" + "\n".join(script_lines)
        return combined_code.strip()

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
