import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class MenuView(View):
    def __init__(self, bot, main_menu=True, prev_menu=None):
        super().__init__()
        self.bot = bot
        self.main_menu = main_menu
        self.prev_menu = prev_menu

        if main_menu:
            self.add_main_buttons()
        else:
            self.add_category_buttons(prev_menu)

    def add_main_buttons(self):
        categories = ["Aanvallen", "Verdedigen", "Kaart", "Farmen", "Rooftochten", "Overig"]
        for category in categories:
            button = Button(label=category, style=discord.ButtonStyle.primary)
            button.callback = self.create_subcategory_view(category)
            self.add_item(button)

    def add_category_buttons(self, category):
        subcategories = {
            "Aanvallen": ["Offpack", "TimeTool"],
            "Verdedigen": ["Defpack", "SnipeTool"],
            "Kaart": ["Mapfunctions", "Overwatch"],
            "Farmen": ["FarmGod", "FarmShaper"],
            "Rooftochten": ["Massa rooftochten", "Roof unlocker"],
            "Overig": ["GS balancer"],
        }

        for subcategory in subcategories.get(category, []):
            button = Button(label=subcategory, style=discord.ButtonStyle.secondary)
            button.callback = self.handle_subcategory(subcategory)
            self.add_item(button)

        # Add a back button to return to the main menu
        back_button = Button(label="Previous", style=discord.ButtonStyle.danger)
        back_button.callback = self.go_back
        self.add_item(back_button)

    def create_subcategory_view(self, category):
        async def callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content=f"{category} Subcategories:", view=MenuView(self.bot, main_menu=False, prev_menu=category))

        return callback

    async def handle_subcategory(self, subcategory):
        async def callback(interaction: discord.Interaction):
            await interaction.response.send_message(f"Selected {subcategory}", ephemeral=True)
        
        return callback

    async def go_back(self, interaction: discord.Interaction):
        if self.main_menu:
            await interaction.response.edit_message(content="Main Menu:", view=MenuView(self.bot))
        else:
            await interaction.response.edit_message(content="Main Menu:", view=MenuView(self.bot))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()  # Sync commands with Discord

@bot.tree.command(name="scripts", description="Displays the script categories")
async def scripts(interaction: discord.Interaction):
    await interaction.response.send_message("Main Menu:", view=MenuView(bot), ephemeral=True)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
