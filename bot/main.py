import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed
from discord.ui import View, Button, Modal, TextInput, Select
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Set the color for the embeds to a yellow sidebar
embed_color = discord.Color.from_rgb(255, 255, 0)

# Define a helper method to create embedded messages
def create_embed(title: str, description: str) -> Embed:
    return Embed(title=title, description=description, color=embed_color)

# Updated descriptions dictionary with only the active scripts
descriptions = {
    # Dictionary content unchanged
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
        categories = ["Must haves", "Aanval", "Verdediging", "Kaart", "Farmen", "Rooftochten", "Overig", "Stats", "Package"]
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
            embed = create_embed(f"**{category} scripts:**", "")
            await interaction.response.edit_message(
                content=None,
                embed=embed,
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

        embed = create_embed("Select the script you want more details about:", "")
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )

class ResultSelectionView(View):
    def __init__(self, bot, results):
        super().__init__(timeout=None)
        self.bot = bot
        self.results = results
        self.add_result_selector()
        self.add_search_again_button()
        self.add_main_menu_button()

    def add_result_selector(self):
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
        embed = create_embed(selected_script, description)
        await interaction.response.edit_message(embed=embed, view=self)

    async def search_again(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SearchModal(self.bot))

    async def go_to_main_menu(self, interaction: discord.Interaction):
        embed = create_embed("Scripts Menu", main_menu_description)
        await interaction.response.edit_message(embed=embed, view=PublicMenuView(self.bot))

class PrivateMenuView(View):
    def __init__(self, bot, category):
        super().__init__(timeout=None)
        self.bot = bot
        self.category = category
        self.add_category_buttons()
        self.add_main_menu_button()

    def add_category_buttons(self):
        subcategories = {
            "Must haves": [
                "Offpack", "Defpack", "TimeTool", "Massa rooftochten", "GS balancer", 
                "SnipeTool", "IncsEnhancer", "TribeShare", "NobleSpam", "CoordFilter", 
                "Coordgrab", "Resource sender", "TribeLines", "Village renamer",
                "MintTimer", "CoinPull", "Munt Enhancer", "Template Enhancer",
                "GroupPlacer", "ClearsTimer", "UnitsDivide"
            ],
            "Aanval": ["Offpack", "TimeTool", "EasyCommand", "NobleSpam", "Template Enhancer", "MobileAttSent"],
            "Verdediging": ["Defpack", "SnipeTool", "TimeTool", "IncsEnhancer", "TribeIncs", "UnitsDivide"],
            "Kaart": ["Mapfunctions", "Overwatch", "CoordGrab", "TribeLines", "ClaimEnhancer"],
            "Farmen": ["FarmGod", "FarmShaper"],
            "Rooftochten": ["Massa rooftochten", "Roof unlocker"],
            "Overig": ["GS balancer", "TribeShare", "CoordFilter", "Resource sender", "Village renamer", "GroupPlacer", "ClearsTimer", "MintTimer", "CoinPull", "Munt Enhancer", "Vlaggen upgrader"],
            "Stats": ["Noble MS", "Troop Counter", "PP Log"],
            "Package": ["Sangu Package"],
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
            embed = create_embed(subcategory, description)
            main_menu_only_view = View()
            main_menu_button = Button(label="Main Menu", style=discord.ButtonStyle.danger)
            main_menu_button.callback = self.go_to_main_menu
            main_menu_only_view.add_item(main_menu_button)

            await interaction.response.edit_message(embed=embed, view=main_menu_only_view)
        return callback

    async def go_to_main_menu(self, interaction: discord.Interaction):
        embed = create_embed("Scripts Menu", main_menu_description)
        await interaction.response.edit_message(embed=embed, view=PublicMenuView(self.bot))

# Purge command with embedded response
@bot.tree.command(name="purge", description="Purge messages in a channel based on various criteria.")
@app_commands.default_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        embed = create_embed("Error", "You do not have permission to use this command.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = create_embed("Purge Options", "Choose a purge option:")
    view = PurgeOptionsView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PurgeOptionsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Purge All Messages", value="purge_all", description="Delete all messages in the channel."),
            discord.SelectOption(label="Purge Number of Messages", value="purge_number", description="Delete a specific number of messages."),
            discord.SelectOption(label="Purge Non-Bot Messages", value="purge_non_bot", description="Delete all messages sent by users."),
            discord.SelectOption(label="Purge Bot Messages", value="purge_bot", description="Delete all messages sent by bots."),
            discord.SelectOption(label="Purge Messages from a User", value="purge_user", description="Delete messages from a specific user."),
            discord.SelectOption(label="Purge Messages from a Timeframe", value="purge_timeframe", description="Delete messages within a timeframe."),
        ]
        super().__init__(placeholder="Select a purge option...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        option = self.values[0]
        if option == "purge_all":
            await self.view.purge_all_messages(interaction)
        elif option == "purge_number":
            await self.view.prompt_number_of_messages(interaction)
        elif option == "purge_non_bot":
            await self.view.purge_non_bot_messages(interaction)
        elif option == "purge_bot":
            await self.view.purge_bot_messages(interaction)
        elif option == "purge_user":
            await self.view.prompt_user_selection(interaction)
        elif option == "purge_timeframe":
            await self.view.prompt_timeframe(interaction)

class PurgeOptionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PurgeOptionsSelect())

    async def purge_all_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        total_deleted = 0
        delay_between_deletions = 1
        command_message_id = interaction.id  # Capture the ID of the message that triggered /purge

        async for message in interaction.channel.history(limit=None):
            if message.id == command_message_id:
                continue  # Skip the /purge command message

            try:
                await message.delete()
                total_deleted += 1
                await asyncio.sleep(delay_between_deletions)  # Delay to avoid rate limits

            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after or 10
                    await asyncio.sleep(retry_after)
                else:
                    break

        embed = create_embed("Purge Complete", f"Deleted {total_deleted} messages.")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def prompt_number_of_messages(self, interaction: discord.Interaction):
        modal = NumberInputModal()
        await interaction.response.send_modal(modal)

    async def purge_non_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        total_deleted = 0
        delay_between_deletions = 1
        command_message_id = interaction.id

        async for message in interaction.channel.history(limit=None):
            if message.id == command_message_id or message.author.bot:
                continue  # Skip the /purge command message and bot messages

            try:
                await message.delete()
                total_deleted += 1
                await asyncio.sleep(delay_between_deletions)

            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after or 10
                    await asyncio.sleep(retry_after)
                else:
                    break

        embed = create_embed("Purge Complete", f"Deleted {total_deleted} non-bot messages.")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def purge_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        total_deleted = 0
        delay_between_deletions = 1
        command_message_id = interaction.id

        async for message in interaction.channel.history(limit=None):
            if message.id == command_message_id or not message.author.bot:
                continue  # Skip the /purge command message and non-bot messages

            try:
                await message.delete()
                total_deleted += 1
                await asyncio.sleep(delay_between_deletions)

            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after or 10
                    await asyncio.sleep(retry_after)
                else:
                    break

        embed = create_embed("Purge Complete", f"Deleted {total_deleted} bot messages.")
        await interaction.followup.send(embed=embed, ephemeral=True)


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
            deleted_count = 0
            command_message_id = interaction.id  # ID of the /purge command

            async for message in interaction.channel.history(limit=limit + 1):
                if message.id == command_message_id:
                    continue  # Skip the /purge command message itself

                if deleted_count < limit:
                    try:
                        await message.delete()
                        deleted_count += 1
                    except discord.HTTPException as e:
                        if e.status == 429:
                            retry_after = e.retry_after or 10
                            await asyncio.sleep(retry_after)
                        else:
                            break
                else:
                    break

            embed = create_embed("Purge Complete", f"Deleted {deleted_count} messages.")
            await interaction.followup.send(embed=embed, ephemeral=True)

        except ValueError:
            embed = create_embed("Error", "Please enter a valid positive integer.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

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
            embed = create_embed("Purge Complete", f"Deleted {len(deleted)} messages from {user.display_name}.")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = create_embed("Error", f"Error: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

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
            embed = create_embed("Purge Complete", f"Deleted {len(deleted)} messages from the last {hours} hours and {minutes} minutes.")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            embed = create_embed("Error", str(e))
            await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()  # Sync commands with Discord

@bot.tree.command(name="scripts", description="Displays the script categories")
async def scripts(interaction: discord.Interaction):
    embed = create_embed("Scripts Menu", main_menu_description)
    await interaction.response.send_message(embed=embed, view=PublicMenuView(bot), ephemeral=True)

@bot.command(name="scripts", help="Displays the description of a specific script by name.")
async def get_script_description(ctx, *, script_name: str):
    script_name = script_name.lower()
    matching_script = next((name for name in descriptions if name.lower() == script_name), None)

    if matching_script:
        embed = create_embed(matching_script, descriptions[matching_script])
        await ctx.send(embed=embed)
    else:
        closest_match, score = process.extractOne(script_name, descriptions.keys())
        if score > 60:
            view = View()
            suggestion_button = Button(label=f"Bedoelde je '{closest_match}'?", style=discord.ButtonStyle.primary)

            async def suggestion_callback(interaction: discord.Interaction):
                embed = create_embed(closest_match, descriptions[closest_match])
                await interaction.response.send_message(embed=embed)

            suggestion_button.callback = suggestion_callback
            view.add_item(suggestion_button)

            embed = create_embed("Script Not Found", f"Script '{script_name}' not found.")
            await ctx.send(embed=embed, view=view)
        else:
            embed = create_embed("Script Not Found", f"Script '{script_name}' not found in the library.")
            await ctx.send(embed=embed)

# AM command with embedded responses
class AMView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_button("Opslag rush", self.opslag_rush_callback)
        self.add_button("ZC rush", self.zc_rush_callback)
        self.add_button("AH rush", self.ah_rush_callback)
        self.add_button("Muur rush", self.muur_rush_callback)
        self.add_button("Toren rush", self.toren_rush_callback)
        self.add_button("Kerk rush", self.kerk_rush_callback)
        self.add_button("Muur spoed", self.muur_spoed_callback)
        self.add_button("OFF sjabloon", self.off_sjabloon_callback)
        self.add_button("DEF sjabloon", self.def_sjabloon_callback)

    def add_button(self, label, callback):
        button = Button(label=label, style=discord.ButtonStyle.primary)
        button.callback = callback
        self.add_item(button)

    async def opslag_rush_callback(self, interaction: Interaction):
        embed = create_embed("Opslag rush", "Placeholder text for Opslag rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def zc_rush_callback(self, interaction: Interaction):
        embed = create_embed("ZC rush", "Placeholder text for ZC rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def ah_rush_callback(self, interaction: Interaction):
        embed = create_embed("AH rush", "Placeholder text for AH rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def muur_rush_callback(self, interaction: Interaction):
        embed = create_embed("Muur rush", "Placeholder text for Muur rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def toren_rush_callback(self, interaction: Interaction):
        embed = create_embed("Toren rush", "Placeholder text for Toren rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def kerk_rush_callback(self, interaction: Interaction):
        embed = create_embed("Kerk rush", "Placeholder text for Kerk rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def muur_spoed_callback(self, interaction: Interaction):
        embed = create_embed("Muur spoed", "Placeholder text for Muur spoed.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def off_sjabloon_callback(self, interaction: Interaction):
        embed = create_embed("OFF sjabloon", "Placeholder text for OFF sjabloon.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def def_sjabloon_callback(self, interaction: Interaction):
        embed = create_embed("DEF sjabloon", "Placeholder text for DEF sjabloon.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="am", description="Displays rush and template options for AM")
async def am(interaction: Interaction):
    embed = create_embed("Choose an action:", "Select one of the options below for more information.")
    await interaction.response.send_message(embed=embed, view=AMView(), ephemeral=True)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
