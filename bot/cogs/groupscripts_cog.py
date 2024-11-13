import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Select
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

# Helper function to combine script codes from selected scripts
def get_combined_script_code(selected_scripts):
    combined_code = "javascript:\n"
    missing_scripts = []  # Track scripts without descriptions

    for script_name in selected_scripts:
        description = descriptions.get(script_name)
        if description:
            # Extract lines that contain $.getScript
            script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript")]
            combined_code += "\n".join(script_lines) + "\n"
            print(f"Found description for {script_name}: Adding to combined code.")
        else:
            # If description is missing, add to missing list and log it
            missing_scripts.append(script_name)
            print(f"No description found for {script_name}: Skipping.")

    return combined_code.strip(), missing_scripts  # Return combined code and list of missing scripts

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command to open the selection view for combining scripts
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
        combine_button.callback = self.show_combined_code
        self.add_item(combine_button)
        print("Added Combine Scripts button")  # Debug print

    async def select_scripts(self, interaction: discord.Interaction):
        # Append selected scripts from dropdown
        selected_values = interaction.data["values"]
        self.selected_scripts.extend(selected_values)
        
        # Remove duplicates
        self.selected_scripts = list(set(self.selected_scripts))
        print(f"Current selected scripts: {self.selected_scripts}")  # Debug print

        # Acknowledge the interaction with a deferred response to avoid "interaction failed"
        await interaction.response.defer() 

    async def show_combined_code(self, interaction: discord.Interaction):
        print("Combine button clicked")  # Debug print
        if not self.selected_scripts:
            await interaction.response.send_message("Geen scripts geselecteerd. Selecteer ten minste één script.", ephemeral=True)
            print("No scripts selected message sent")  # Debug print
        else:
            combined_code, missing_scripts = get_combined_script_code(self.selected_scripts)
            
            # Notify user if there are missing scripts
            if missing_scripts:
                missing_msg = f"De volgende scripts konden niet worden gevonden en zijn overgeslagen: {', '.join(missing_scripts)}"
                await interaction.followup.send(missing_msg, ephemeral=True)
                print(f"Missing scripts: {missing_scripts}")

            # Check if combined code is empty after skipping missing descriptions
            if not combined_code:
                await interaction.followup.send("Geen geldige scripts gevonden om te combineren.", ephemeral=True)
                print("No valid script lines found in descriptions.")
                return

            # Split the message if it exceeds Discord's limits
            code_chunks = [combined_code[i:i+2000] for i in range(0, len(combined_code), 2000)]
            
            for index, chunk in enumerate(code_chunks, start=1):
                embed = create_embed(
                    title=f"Gecombineerde scriptcode - Deel {index}",
                    description=f"```js\n{chunk}\n```"
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                print(f"Sent code chunk {index} to user")  # Debug print

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
