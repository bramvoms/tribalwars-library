import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Select, Button
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="group_scripts", description="Groepeer scripts tot één om laadtijden te bevoorderen.")
    async def group_scripts(self, interaction: discord.Interaction):
        # Defer the interaction to acknowledge it
        await interaction.response.defer()

        # Create a view with script selections and a combine button
        view = ScriptCombineView(interaction.user)  # Pass the command initiator to the view
        embed = create_embed("Selecteer scripts om te groeperen", "Selecteer de scripts en klik op groeperen om de code in DM gestuurd te krijgen.")
        await interaction.followup.send(embed=embed, view=view)

class ScriptCombineView(View):
    def __init__(self, command_user):
        super().__init__(timeout=None)
        self.command_user = command_user  # Store the user who sent the command
        self.selected_scripts = set()  # Track selected scripts

        # Divide scripts into chunks of 20 for multiple selection menus
        script_chunks = [list(descriptions.keys())[i:i + 20] for i in range(0, len(descriptions), 20)]
        
        # Create a Select menu for each chunk
        for i, chunk in enumerate(script_chunks, start=1):
            options = [discord.SelectOption(label=script, value=script) for script in chunk]
            select = Select(placeholder=f"Select scripts (Group {i})", options=options, min_values=0, max_values=len(options))
            select.callback = self.update_selected_scripts
            self.add_item(select)

        # Add the "Combine Now" button to finalize the selection and send combined code
        combine_button = Button(label="Groeperen", style=discord.ButtonStyle.success)
        combine_button.callback = self.send_combined_code
        self.add_item(combine_button)

        # Add "Clear Selection" button to reset selections
        clear_button = Button(label="Selectie wissen", style=discord.ButtonStyle.danger)
        clear_button.callback = self.clear_selection
        self.add_item(clear_button)

        # Add "Delete Message" button to delete the interaction message
        delete_button = Button(label="Verwijder bericht", style=discord.ButtonStyle.danger)
        delete_button.callback = self.delete_message
        self.add_item(delete_button)

    async def update_selected_scripts(self, interaction: discord.Interaction):
        # Check if the user is the command initiator
        if interaction.user != self.command_user:
            await interaction.response.send_message("You are not authorized to select scripts for this action.", ephemeral=True)
            return

        # Update selected scripts based on current selections in all menus
        selected_values = set(interaction.data["values"])
        self.selected_scripts.symmetric_difference_update(selected_values)

        # Keep selected options highlighted
        for select in self.children:
            if isinstance(select, Select):
                for option in select.options:
                    option.default = option.value in self.selected_scripts

        # Respond to interaction by editing the message to update view
        await interaction.response.edit_message(view=self)
    
    async def clear_selection(self, interaction: discord.Interaction):
        # Check if the user is the command initiator
        if interaction.user != self.command_user:
            await interaction.response.send_message("You are not authorized to clear selections.", ephemeral=True)
            return

        # Clear the selected scripts
        self.selected_scripts.clear()

        # Reset all options to not be highlighted
        for select in self.children:
            if isinstance(select, Select):
                for option in select.options:
                    option.default = False

        # Edit the interaction message to reflect cleared selection
        await interaction.response.edit_message(content="Selection cleared. Please select scripts to combine again.", view=self)

    async def send_combined_code(self, interaction: discord.Interaction):
        # Check if the user is the command initiator
        if interaction.user != self.command_user:
            await interaction.response.send_message("You are not authorized to combine scripts.", ephemeral=True)
            return

        if not self.selected_scripts:
            await interaction.response.send_message("No scripts selected. Please select at least one script.", ephemeral=True)
            return

        # Generate the combined script code
        combined_code = self.get_combined_script_code()

         # Use the pre-configured embed style from main.py
        embed = create_embed(
            title="Gegroepeerde Script Code",
            description=f"Hier is je gegroepeerde script:\n```js\n{combined_code}\n```"
        )

        # Send the embedded message to the user's DM
        try:
            user_dm = await interaction.user.create_dm()
            await user_dm.send(embed=embed)
            await interaction.response.send_message("Het gegroepeerde script is naar je DM verzonden.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error sending DM: {e}", ephemeral=True)

    async def delete_message(self, interaction: discord.Interaction):
        # Check if the user is the command initiator
        if interaction.user != self.command_user:
            await interaction.response.send_message("You are not authorized to delete this message.", ephemeral=True)
            return

        # Delete the interaction message
        await interaction.message.delete()

    def get_combined_script_code(self):
        # Define a specific order for prioritized scripts
        prioritized_scripts = ["Millisecond tagger", "Timetool"]
        
        # Start the combined code string with JavaScript label
        combined_code = "javascript:\n"

        # Sort selected scripts so prioritized scripts appear first if selected
        ordered_scripts = sorted(self.selected_scripts, key=lambda x: (x not in prioritized_scripts, prioritized_scripts.index(x) if x in prioritized_scripts else float('inf')))

        # Add each script to the combined code
        for script_name in ordered_scripts:
            description = descriptions.get(script_name)
            if description:
                # Extract script URLs and variables, if any
                script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript") or "var" in line]
                combined_code += "\n".join(script_lines) + "\n"

        return combined_code.strip()

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
