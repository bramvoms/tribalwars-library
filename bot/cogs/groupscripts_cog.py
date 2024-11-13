import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Select
from cogs.scripts_cog import descriptions  # Import descriptions from scripts_cog
from main import create_embed

# Helper function to combine script codes from selected scripts
def get_combined_script_code(selected_scripts):
    combined_code = "javascript:\n"
    missing_scripts = []

    for script_name in selected_scripts:
        description = descriptions.get(script_name)
        if description:
            # Extract lines containing $.getScript
            script_lines = [line.strip() for line in description.splitlines() if line.strip().startswith("$.getScript")]
            combined_code += "\n".join(script_lines) + "\n"
            print(f"Added {script_name} to combined code.")
        else:
            missing_scripts.append(script_name)
            print(f"{script_name} missing description.")

    return combined_code.strip(), missing_scripts

class GroupScriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command to open script selection
    @app_commands.command(name="group_scripts", description="Combine scripts into a single script for faster loading.")
    async def group_scripts(self, interaction: discord.Interaction):
        print("Group scripts command triggered.")
        await interaction.response.defer(ephemeral=True)

        # Send the view for script selection
        try:
            await interaction.followup.send("Selecteer scripts om te combineren:", view=ScriptCombineView(self.bot))
            print("Script selection view sent to user.")
        except Exception as e:
            print(f"Error sending script selection view: {e}")

class ScriptCombineView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.selected_scripts = []
        print("Initialized ScriptCombineView")

        # Add dropdowns for script selection
        options = [discord.SelectOption(label=script_name) for script_name in descriptions.keys()]
        select = Select(placeholder="Selecteer scripts", options=options, min_values=1, max_values=len(options))
        select.callback = self.select_scripts
        self.add_item(select)

        # Combine button to finalize selection
        combine_button = Button(label="Combineer Geselecteerde Scripts", style=discord.ButtonStyle.success)
        combine_button.callback = self.show_combined_code
        self.add_item(combine_button)
        print("Combine Scripts button added")

    async def select_scripts(self, interaction: discord.Interaction):
        # Record selected scripts
        self.selected_scripts = interaction.data["values"]
        print(f"Scripts selected: {self.selected_scripts}")
        
        # Acknowledge interaction
        await interaction.response.defer()

    async def show_combined_code(self, interaction: discord.Interaction):
        print("Combine button clicked.")
        if not self.selected_scripts:
            await interaction.response.send_message("Geen scripts geselecteerd. Selecteer ten minste één script.", ephemeral=True)
            print("No scripts selected message sent.")
        else:
            combined_code, missing_scripts = get_combined_script_code(self.selected_scripts)
            
            # Send missing script information if any
            if missing_scripts:
                missing_msg = f"De volgende scripts zijn niet gevonden en overgeslagen: {', '.join(missing_scripts)}"
                await interaction.followup.send(missing_msg, ephemeral=True)
                print(f"Missing scripts: {missing_scripts}")

            # Check if combined code is empty
            if not combined_code:
                await interaction.followup.send("Geen geldige scripts gevonden om te combineren.", ephemeral=True)
                print("No valid script lines found.")
                return

            # Split the code if it's too long
            code_chunks = [combined_code[i:i+2000] for i in range(0, len(combined_code), 2000)]
            for index, chunk in enumerate(code_chunks, start=1):
                embed = create_embed(
                    title=f"Gecombineerde scriptcode - Deel {index}",
                    description=f"```js\n{chunk}\n```"
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                print(f"Sent code chunk {index} to user")

async def setup(bot):
    await bot.add_cog(GroupScriptsCog(bot))
