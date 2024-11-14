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
        delay_between_deletions = 1.5  # Conservative delay to avoid rate limits

        async for message in interaction.channel.history(limit=None):
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

        # Send an ephemeral follow-up message to the user with the total deleted count
        await interaction.followup.send(f"Purge complete: Deleted {total_deleted} messages.", ephemeral=True)

    async def prompt_number_of_messages(self, interaction: discord.Interaction):
        modal = NumberInputModal()
        await interaction.response.send_modal(modal)

    async def purge_non_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        total_deleted = 0
        delay_between_deletions = 1.5

        async for message in interaction.channel.history(limit=None):
            if message.author.bot:
                continue  # Skip bot messages

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

        # Send an ephemeral follow-up message to the user with the total deleted count
        await interaction.followup.send(f"Purge complete: Deleted {total_deleted} non-bot messages.", ephemeral=True)

    async def purge_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        total_deleted = 0
        delay_between_deletions = 1.5

        async for message in interaction.channel.history(limit=None):
            if not message.author.bot:
                continue  # Skip non-bot messages

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

        # Send an ephemeral follow-up message to the user with the total deleted count
        await interaction.followup.send(f"Purge complete: Deleted {total_deleted} bot messages.", ephemeral=True)

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

class NumberInputModal(Modal, title="Purge number of messages"):
    number = TextInput(label="Number of messages to delete", placeholder="Enter a number (e.g., 10)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.number.value)
            if limit <= 0:
                raise ValueError("Number must be positive.")

            await interaction.response.defer(thinking=True)
            deleted_count = 0
            delay_between_deletions = 1.5  # Conservative delay to avoid rate limits

            async for message in interaction.channel.history(limit=limit):
                try:
                    await message.delete()
                    deleted_count += 1
                    await asyncio.sleep(delay_between_deletions)
                except discord.HTTPException as e:
                    if e.status == 429:
                        retry_after = e.retry_after or 10
                        await asyncio.sleep(retry_after)
                    else:
                        break

            # Send an ephemeral follow-up message with the total deleted count
            await interaction.followup.send(f"Purge complete: Deleted {deleted_count} messages.", ephemeral=True)

        except ValueError:
            embed = create_embed("Error", "Please enter a valid positive integer.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(PurgeCog(bot))
