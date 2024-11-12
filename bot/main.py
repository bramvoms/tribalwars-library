import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Multi-line descriptions with triple quotes for each subcategory
descriptions = {
    "Offpack": """Offpack is een verzameling van meerdere functionaliteiten die samen komen tot één script die je helpt bij het versturen van aanvallen.

Een van de functionaliteiten is de mass attack planner.

Een andere functionaliteit is het automatisch invullen van troepen sjablonen.

```js
// Example JavaScript snippet
function attackPlanner() {
    console.log("Planning attack...");
}
```""",
    
    "TimeTool": """TimeTool: Helps in accurately timing attacks.

With this tool, you can precisely coordinate your attack timings, allowing you to execute 
multiple attacks with pinpoint accuracy. Perfect for competitive players.""",
    # Other descriptions...
}

class PublicMenuView(View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.add_main_buttons()

    def add_main_buttons(self):
        categories = ["Aanvallen", "Verdedigen", "Kaart", "Farmen", "Rooftochten", "Overig"]
        for category in categories:
            button = Button(label=category, style=discord.ButtonStyle.primary)
            button.callback = self.show_private_menu(category)
            self.add_item(button)

    def show_private_menu(self, category):
        async def callback(interaction: discord.Interaction):
            await interaction.response.send_message(
                content=f"{category} Subcategories:",
                view=PrivateMenuView(self.bot, category),
                ephemeral=True
            )
        return callback

class PrivateMenuView(View):
    def __init__(self, bot, category):
        super().__init__()
        self.bot = bot
        self.category = category
        self.add_category_buttons()

    def add_category_buttons(self):
        subcategories = {
            "Aanvallen": ["Offpack", "TimeTool"],
            "Verdedigen": ["Defpack", "SnipeTool"],
            "Kaart": ["Mapfunctions", "Overwatch"],
            "Farmen": ["FarmGod", "FarmShaper"],
            "Rooftochten": ["Massa rooftochten", "Roof unlocker"],
            "Overig": ["GS balancer"],
        }

        for subcategory in subcategories.get(self.category, []):
            button = Button(label=subcategory, style=discord.ButtonStyle.secondary)
            button.callback = self.show_subcategory_description(subcategory)
            self.add_item(button)

        # Add a back button to return to the main menu
        back_button = Button(label="Previous", style=discord.ButtonStyle.danger)
        back_button.callback = self.go_back
        self.add_item(back_button)

    def show_subcategory_description(self, subcategory):
        async def callback(interaction: discord.Interaction):
            description = descriptions.get(subcategory, "No description available.")
            await interaction.response.send_message(f"{subcategory}:\n{description}", ephemeral=True)
        
        return callback

    async def go_back(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Main Menu:", view=PublicMenuView(self.bot))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()  # Sync commands with Discord

# Define the command with an administrator check
@bot.tree.command(name="scripts", description="Displays the script categories")
@app_commands.checks.has_permissions(administrator=True)
async def scripts(interaction: discord.Interaction):
    # Defer the interaction response to prevent "User used /scripts" message
    await interaction.response.defer(ephemeral=True)
    
    # Send an embedded message as a regular bot message
    embed = discord.Embed(
        title="Scripts Menu",
        description="Select a category to explore the available scripts.",
        color=discord.Color.blue()
    )
    await interaction.channel.send(embed=embed, view=PublicMenuView(bot))

# Error handler for when a user lacks administrator permissions
@scripts.error
async def scripts_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "You do not have permission to use this command. Administrator access is required.",
            ephemeral=True
        )

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
