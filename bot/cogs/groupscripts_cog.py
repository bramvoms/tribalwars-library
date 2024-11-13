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
        # Defer the interaction to acknowledge it
        await interaction.response.defer()

        # Create a view with script selections and a combine button
        view = ScriptCombineView(interaction)  # Pass interaction to view for deletion
        embed = create_embed("Select Scripts to Combine", "Select scripts and click 'Combine Now' to receive the combined code in your DMs.")
        await interaction.followup.send(embed=embed, view=view)

class ScriptCombineView(View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.selected_scripts = set()  # Track selected scripts
        self.interaction = interaction  # Store interaction for message deletion

        # Divide scripts into chunks of 20 for multiple selection menus
        script_chunks = [list(descriptions.keys())[i:i + 20] for i in range(0, len(descriptions), 20)]
        
        # Create a Select menu for each chunk
        for i, chunk in enumerate(script_chunks, start=1):
            options = [discord.SelectOption(label=script, value=script) for script in chunk]
            select = Select(placeholder=f"Select scripts (Group {i})", options=options, min_values=0, max_values=len(options))
            select.callback = self.update_selected_scripts
            self.add_item(select)

        # Add the "Combine Now" button to finalize the selection and send combined code
        combine_button = Button(label="Combine Now", style=discord.ButtonStyle.success)
        combine_button.callback = self.send_combined_code
        self.add_item(combine_button)

    async def update_selected_scripts(self, interaction: discord.Interaction):
        # Update selected scripts based on current selections in all menus
        selected_values = set(interaction.data["values"])
        self.selected_scripts.symmetric_difference_update(selected_values)

        # Keep selected options highlighted
        for select in self.children:
            if isinstance(select, Select):
                for option in select.options:
                    option.default = option.value in self.selected_scripts

        await interaction.response.defer()  # Defer the response to keep interaction active

    async def send_combined_code(self, interaction: discord.Interaction):
        if not self.selected_scripts:
            await interaction.response.send_message("No scripts selected. Please select at least one script.", ephemeral=True)
            return

        # Generate the combined script code
        combined_code = self.get_combined_script_code()

        # Send the combined code to the user's DM
        try:
            user_dm = await interaction.user.create_dm()
            await user_dm.send(f"Here is your combined script code:\n```js\n{combined_code}\n```")
            await interaction.followup.send("The combined script code has been sent to your DMs.", ephemeral=True)

            # Delete the message in the channel
            original_message = await self.interaction.original_response()
            await original_message.delete()
        except Exception as e:
            await interaction.followup.send(f"Error sending DM: {e}", ephemeral=True)

    def get_combined_script_code(self):
        # Combine the selected scripts into the final code
        combined_code = "javascript:\n"
        for script_name in self.selected_scripts:
            description = descriptions.get(script_name)
            if description:
                # Extract script URLs and variables, if any
                script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript") or "var" in line]
                combined_code += "\n".join(script_lines) + "\n"
        return combined_code.strip()

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
