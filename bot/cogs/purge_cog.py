import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Select, Modal, TextInput
import asyncio
from main import create_embed

class PurgeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="purge", description="Purge messages in a channel based on various criteria.")
    @app_commands.default_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            embed = create_embed("Error", "You do not have permission to use this command.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = create_embed("Purge Options", "Choose a purge option:")
        view = PurgeOptionsView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PurgeOptionsView(View):
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

        embed = create_embed("Purge complete", f"Deleted {total_deleted} messages.")
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

        embed = create_embed("Purge complete", f"Deleted {total_deleted} non-bot messages.")
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

        embed = create_embed("Purge complete", f"Deleted {total_deleted} bot messages.")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def prompt_user_selection(self, interaction: discord.Interaction):
        modal = UserSelectionModal()
        await interaction.response.send_modal(modal)

    async def prompt_timeframe(self, interaction: discord.Interaction):
        modal = TimeframeModal()
        await interaction.response.send_modal(modal)

class PurgeOptionsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Purge all messages", value="purge_all", description="Delete all messages in the channel."),
            discord.SelectOption(label="Purge number of messages", value="purge_number", description="Delete a specific number of messages."),
            discord.SelectOption(label="Purge non-bot messages", value="purge_non_bot", description="Delete all messages sent by users."),
            discord.SelectOption(label="Purge bot messages", value="purge_bot", description="Delete all messages sent by bots."),
            discord.SelectOption(label="Purge messages from a user", value="purge_user", description="Delete messages from a specific user."),
            discord.SelectOption(label="Purge messages from a timeframe", value="purge_timeframe", description="Delete messages within a timeframe."),
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

class NumberInputModal(Modal, title="Purge number of messages"):
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

            embed = create_embed("Purge complete", f"Deleted {deleted_count} messages.")
            await interaction.followup.send(embed=embed, ephemeral=True)

        except ValueError:
            embed = create_embed("Error", "Please enter a valid positive integer.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

class UserSelectionModal(Modal, title="Purge messages from a User"):
    user_input = TextInput(label="User ID or mention", placeholder="Enter the user's ID or mention them", required=True)

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
            embed = create_embed("Purge complete", f"Deleted {len(deleted)} messages from {user.display_name}.")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = create_embed("Error", f"Error: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

class TimeframeModal(Modal, title="Purge Messages from a Timeframe"):
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
            embed = create_embed("Purge complete", f"Deleted {len(deleted)} messages from the last {hours} hours and {minutes} minutes.")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            embed = create_embed("Error", str(e))
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(PurgeCog(bot))

