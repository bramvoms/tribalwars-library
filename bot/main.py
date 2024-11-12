import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from discord import app_commands
from fuzzywuzzy import fuzz
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Updated descriptions dictionary with only the active scripts
descriptions = {
    "Offpack": "Offpack is a collection of functionalities to help send attacks efficiently.",
    "TimeTool": "TimeTool helps in accurately timing attacks, allowing for synchronized actions.",
    "Defpack": "Defpack organizes defensive troops for optimal distribution in defense.",
    "SnipeTool": "SnipeTool assists in setting up snipes to defend against incoming attacks.",
    "Mapfunctions": "Mapfunctions provides various tools to enhance the TribalWars map display.",
    "Overwatch": "Overwatch helps monitor villages and activities on the map.",
    "FarmGod": "FarmGod is an automated farming tool to maximize resource gains from farming.",
    "FarmShaper": "FarmShaper organizes and optimizes your farming lists for efficient resource gathering.",
    "Massa rooftochten": "Massa rooftochten simplifies mass scavenging operations for quick loot gathering.",
    "Roof unlocker": "Roof unlocker unlocks the scavenging feature in mass amounts for faster setup.",
    "GS balancer": "GS balancer balances and redistributes resources across villages efficiently.",
    "Noble MS": "Noble MS provides millisecond-level precision for noble timing and coordination.",
    "Troop Counter": "Troop Counter counts and organizes troop levels across all villages.",
    "Sangu Package": "Sangu Package includes a suite of tools to enhance gameplay, like map tools and overviews.",
    "EasyCommand": "EasyCommand simplifies troop command issuing across multiple villages.",
}

main_menu_description = """**TribalWars Library: Scripts**

Gebruik de knoppen hieronder om een categorie en daarna het script te selecteren waar je uitleg over wilt."""

class PublicMenuView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_main_buttons()
        self.add_search_button()

    def add_main_buttons(self):
        categories = ["Aanvallen", "Verdedigen", "Kaart", "Farmen", "Rooftochten", "Overig", "Stats", "Package"]
        for category in categories:
            button = Button(label=category, style=discord.ButtonStyle.primary)
            button.callback = self.show_private_menu(category)
            self.add_item(button)

    def add_search_button(self):
        search_button = Button(label="Search", style=discord.ButtonStyle.secondary)
        search_button.callback = self.show_search_modal
        self.add_item(search_button)

    def show_private_menu(self, category):
        async def callback(interaction: discord.Interaction):
            await interaction.response.edit_message(
                content=f"**{category} Subcategories:**",
                embed=None,
                view=PrivateMenuView(self.bot, category)
            )
        return callback

    async def show_search_modal(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SearchModal(self.bot))

class SearchModal(Modal):
    def __init__(self, bot):
        super().__init__(title="Search Scripts")
        self.bot = bot
        self.query = TextInput(label="Enter script name or keyword", placeholder="e.g., Offpack")
        self.add_item(self.query)

    async def on_submit(self, interaction: discord.Interaction):
        query = self.query.value.lower()
        results = []

        # Step 1: Exact match check
        if query in descriptions:
            results.append((query, descriptions[query]))
        else:
            # Step 2: Advanced matching with substring and fuzzy matching
            matches = []
            for subcategory, description in descriptions.items():
                subcategory_lower = subcategory.lower()
                description_lower = description.lower()

                # Direct substring match
                if query in subcategory_lower or query in description_lower:
                    matches.append((subcategory, description, 90))  # High priority for direct substring matches

                # Fuzzy match with a lower threshold
                else:
                    score = max(fuzz.partial_ratio(query, subcategory_lower), fuzz.token_set_ratio(query, subcategory_lower))
                    if score > 50:
                        matches.append((subcategory, description, score))  # Priority based on fuzzy score

            # Sort matches by score to prioritize closer matches
            matches = sorted(matches, key=lambda x: x[2], reverse=True)

            # Remove duplicates and keep only the subcategory and description fields
            results = [(subcategory, description) for subcategory, description, _ in matches]

        # Limit the output to the top 2 results
        top_results = results[:2]

        # Create the view with top results
        view = ResultSelectionView(self.bot, top_results)

        await interaction.response.edit_message(
            content="Select the script you want more details about:",
            embed=None,
            view=view
        )

class ResultSelectionView(View):
    def __init__(self, bot, results):
        super().__init__(timeout=None)
        self.bot = bot  # Store the bot instance
        self.results = results
        self.add_result_selector()
        # Add "Search Again" button
        self.add_search_again_button()
        # Add "Main Menu" button
        self.add_main_menu_button()

    def add_result_selector(self):
        # Limit descriptions to 100 characters
        options = [
            discord.SelectOption(label=subcategory, description=(description[:97] + "..." if len(description) > 100 else description))
            for subcategory, description in self.results
        ]
        select = Select(placeholder="Choose a script...", options=options)
        select.callback = self.show_description
        self.add_item(select)

    def add_search_again_button(self):
        search_again_button = Button(label="Search Again", style=discord.ButtonStyle.primary)
        search_again_button.callback = self.search_again
        self.add_item(search_again_button)

    def add_main_menu_button(self):
        main_menu_button = Button(label="Main Menu", style=discord.ButtonStyle.danger)
        main_menu_button.callback = self.go_to_main_menu
        self.add_item(main_menu_button)

    async def show_description(self, interaction: discord.Interaction):
        selected_script = interaction.data["values"][0]
        description = descriptions.get(selected_script, "No description available.")
        # Update the message with the script description and keep the current view
        await interaction.response.edit_message(
            content=f"**{selected_script}**:\n{description}",
            embed=None,
            view=self
        )

    async def search_again(self, interaction: discord.Interaction):
        # Reopen the search modal to allow the user to search again
        await interaction.response.send_modal(SearchModal(self.bot))

    async def go_to_main_menu(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Scripts Menu",
            description=main_menu_description,
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=PublicMenuView(self.bot)
        )

class PrivateMenuView(View):
    def __init__(self, bot, category):
        super().__init__(timeout=None)
        self.bot = bot
        self.category = category
        self.add_category_buttons()
        self.add_main_menu_button()

    def add_category_buttons(self):
        subcategories = {
            "Aanvallen": ["Offpack", "TimeTool"],
            "Verdedigen": ["Defpack", "SnipeTool"],
            "Kaart": ["Mapfunctions", "Overwatch"],
            "Farmen": ["FarmGod", "FarmShaper"],
            "Rooftochten": ["Massa rooftochten", "Roof unlocker"],
            "Overig": ["GS balancer"],
            "Stats": ["Noble MS", "Troop Counter"],
            "Package": ["Sangu Package", "EasyCommand"]
        }

        for subcategory in subcategories.get(self.category, []):
            button = Button(label=subcategory, style=discord.ButtonStyle.secondary)
            button.callback = self.show_subcategory_description(subcategory)
            self.add_item(button)

    def add_main_menu_button(self):
        main_menu_button = Button(label="Main Menu", style=discord.ButtonStyle.danger)
        main_menu_button.callback = self.go_to_main_menu
        self.add_item(main_menu_button)

    def show_subcategory_description(self, subcategory):
        async def callback(interaction: discord.Interaction):
            description = descriptions.get(subcategory, "No description available.")
            await interaction.response.edit_message(
                content=f"**{subcategory}**:\n{description}",
                embed=None,
                view=self
            )
        return callback

    async def go_to_main_menu(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Scripts Menu",
            description=main_menu_description,
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=PublicMenuView(self.bot)
        )

# Add the purge command
@bot.tree.command(name="purge", description="Purge messages in a channel based on various criteria.")
@app_commands.default_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction):
    # Check if the user has permission to manage messages
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    # Present options to the user
    view = PurgeOptionsView()
    await interaction.response.send_message("Choose a purge option:", view=view, ephemeral=True)

class PurgeOptionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Select a purge option...",
        options=[
            discord.SelectOption(label="Purge All Messages", value="purge_all", description="Delete all messages in the channel."),
            discord.SelectOption(label="Purge Number of Messages", value="purge_number", description="Delete a specific number of messages."),
            discord.SelectOption(label="Purge Non-Bot Messages", value="purge_non_bot", description="Delete all messages sent by users."),
            discord.SelectOption(label="Purge Bot Messages", value="purge_bot", description="Delete all messages sent by bots."),
            discord.SelectOption(label="Purge Messages from a User", value="purge_user", description="Delete messages from a specific user."),
            discord.SelectOption(label="Purge Messages from a Timeframe", value="purge_timeframe", description="Delete messages within a timeframe."),
        ]
    )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        option = select.values[0]
        if option == "purge_all":
            await self.purge_all_messages(interaction)
        elif option == "purge_number":
            await self.prompt_number_of_messages(interaction)
        elif option == "purge_non_bot":
            await self.purge_non_bot_messages(interaction)
        elif option == "purge_bot":
            await self.purge_bot_messages(interaction)
        elif option == "purge_user":
            await self.prompt_user_selection(interaction)
        elif option == "purge_timeframe":
            await self.prompt_timeframe(interaction)

    async def purge_all_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        deleted = await interaction.channel.purge()
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

    async def prompt_number_of_messages(self, interaction: discord.Interaction):
        modal = NumberInputModal()
        await interaction.response.send_modal(modal)

    async def purge_non_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        deleted = await interaction.channel.purge(limit=None, check=lambda m: not m.author.bot)
        await interaction.followup.send(f"Deleted {len(deleted)} non-bot messages.", ephemeral=True)

    async def purge_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        deleted = await interaction.channel.purge(limit=None, check=lambda m: m.author.bot)
        await interaction.followup.send(f"Deleted {len(deleted)} bot messages.", ephemeral=True)

    async def prompt_user_selection(self, interaction: discord.Interaction):
        modal = UserSelectionModal()
        await interaction.response.send_modal(modal)

    async def prompt_timeframe(self, interaction: discord.Interaction):
        modal = TimeframeModal()
        await interaction.response.send_modal(modal)

class NumberInputModal(discord.ui.Modal, title="Purge Number of Messages"):
    number = TextInput(label="Number of messages to delete", placeholder="Enter a number (e.g., 10)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.number.value)
            if limit <= 0:
                raise ValueError("Number must be positive.")
            await interaction.response.defer(thinking=True)
            deleted = await interaction.channel.purge(limit=limit)
            await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Please enter a valid positive integer.", ephemeral=True)

class UserSelectionModal(discord.ui.Modal, title="Purge Messages from a User"):
    user_input = TextInput(label="User ID or Mention", placeholder="Enter the user's ID or mention them", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_value = self.user_input.value.strip()
            user = None
            if user_value.isdigit():
                user = await interaction.guild.fetch_member(int(user_value))
            elif user_value.startswith("<@") and user_value.endswith(">"):
                user_id = int(user_value.strip("<@!>"))
                user = await interaction.guild.fetch_member(user_id)
            else:
                user = interaction.guild.get_member_named(user_value)
            if user is None:
                raise ValueError("User not found.")

            await interaction.response.defer(thinking=True)
            deleted = await interaction.channel.purge(limit=None, check=lambda m: m.author == user)
            await interaction.followup.send(f"Deleted {len(deleted)} messages from {user.display_name}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

class TimeframeModal(discord.ui.Modal, title="Purge Messages from a Timeframe"):
    hours = TextInput(label="Hours", placeholder="Enter the number of hours", required=False)
    minutes = TextInput(label="Minutes", placeholder="Enter the number of minutes", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            hours = int(self.hours.value) if self.hours.value else 0
            minutes = int(self.minutes.value) if self.minutes.value else 0
            if hours == 0 and minutes == 0:
                raise ValueError("Please enter a valid timeframe.")

            from datetime import datetime, timedelta

            time_limit = datetime.utcnow() - timedelta(hours=hours, minutes=minutes)

            await interaction.response.defer(thinking=True)
            deleted = await interaction.channel.purge(after=time_limit)
            await interaction.followup.send(f"Deleted {len(deleted)} messages from the last {hours} hours and {minutes} minutes.", ephemeral=True)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()  # Sync commands with Discord

@bot.tree.command(name="scripts", description="Displays the script categories")
async def scripts(interaction: discord.Interaction):
    # Send an embedded message as a regular bot message with a description
    embed = discord.Embed(
        title="Scripts Menu",
        description=main_menu_description,
        color=discord.Color.blue()
    )
    view = PublicMenuView(bot)
    await interaction.response.send_message(embed=embed, view=view)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
