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
    
    "Defpack": """Defpack: Organizes defensive troops for optimal defense.

Use this tool to streamline your defensive setup and improve village resilience. 
Defpack assists in maximizing defensive potential across all units.""",
    
    "SnipeTool": """SnipeTool: Assists in setting up snipes to defend against attacks.

This tool is tailored to help you defend by intercepting incoming attacks. 
Essential for timing snipes and avoiding unexpected losses.""",
    
    "Mapfunctions": """Mapfunctions: Provides various mapping functionalities for better strategy.

Enhance your tactical view of the battlefield with Mapfunctions. 
Get insights into enemy positions, resource spots, and much more.""",
    
    "Overwatch": """Overwatch: Monitors enemy movements on the map.

Stay alert with Overwatch, a tool that keeps track of enemy activities and helps you anticipate threats. 
Best for strategic players who like staying ahead of their opponents.""",
    
    "FarmGod": """FarmGod: Automates and optimizes your farming routines.

FarmGod simplifies the process of resource gathering by automating farms, 
making it easier to acquire resources with minimal effort.""",
    
    "FarmShaper": """FarmShaper: Shapes and prioritizes farms based on resources.

FarmShaper helps you target the most resource-rich farms, saving time and maximizing yields. 
Ideal for efficient farming and resource management.""",
    
    "Massa rooftochten": """Massa rooftochten: Mass raid tool to manage multiple attacks.

Coordinate numerous raids simultaneously, ensuring a high rate of successful resource plundering. 
Perfect for players looking to expand their resource base quickly.""",
    
    "Roof unlocker": """Roof unlocker: Unlocks additional raiding capabilities.

Roof unlocker adds new functionalities to raiding, enabling players to execute advanced raid strategies 
and unlock new levels of efficiency.""",
    
    "GS balancer": """GS balancer: Balances resources across villages.

This tool automates resource balancing across your villages, ensuring steady growth and stability. 
GS balancer is essential for maintaining an even distribution of resources."""
}

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
            await interaction.response.edit_message(content=None, view=MenuView(self.bot, main_menu=False, prev_menu=category))

        return callback

    def handle_subcategory(self, subcategory):
        async def callback(interaction: discord.Interaction):
            description = descriptions.get(subcategory, "No description available.")
            await interaction.response.send_message(f"{subcategory}:\n{description}", ephemeral=True)
        
        return callback

    async def go_back(self, interaction: discord.Interaction):
        if self.main_menu:
            await interaction.response.edit_message(content=None, view=MenuView(self.bot))
        else:
            await interaction.response.edit_message(content=None, view=MenuView(self.bot))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()  # Sync commands with Discord

@bot.tree.command(name="scripts", description="Displays the script categories")
async def scripts(interaction: discord.Interaction):
    await interaction.response.send_message(view=MenuView(bot), ephemeral=True)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
