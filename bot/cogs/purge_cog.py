import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Modal, TextInput
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
        self.stop_deletion = False  # Initialize stop flag
        self.add_item(PurgeOptionsSelect())

    async def purge_all_messages(self, interaction: discord.Interaction):
        embed = create_embed(
            "⚠️ Confirm Purge All",
            "You are about to delete **all messages** in this channel. This action is irreversible. Do you want to continue?"
        )
        view = ConfirmPurgeAllView(self, command_message_id=interaction.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def perform_purge_with_stop(self, interaction: discord.Interaction, check_func):
        """Perform the purge with a 'Stop' button to allow the user to halt purging."""
        total_deleted = 0
        delay_between_deletions = 1.5

        # Create a status message with a 'Stop' button
        status_view = StopPurgeView(self)
        status_message = await interaction.followup.send("Deleting messages...", view=status_view)

        async for message in interaction.channel.history(limit=None):
            if self.stop_deletion or message.id >= interaction.id:  # Only delete messages before command message
                break
            if not check_func(message):
                continue  # Skip messages that do not match the criteria

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

        final_text = f"Purge complete: Deleted {total_deleted} messages." if not self.stop_deletion else f"Purge stopped: {total_deleted} messages deleted."
        await status_message.edit(content=final_text, view=None)

    async def purge_non_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.perform_purge_with_stop(interaction, check_func=lambda m: not m.author.bot)

    async def purge_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.perform_purge_with_stop(interaction, check_func=lambda m: m.author.bot)

    async def prompt_number_of_messages(self, interaction: discord.Interaction):
        modal = NumberInputModal(command_message_id=interaction.id)
        await interaction.response.send_modal(modal)

    async def purge_messages_from_user(self, interaction: discord.Interaction):
        modal = UserSelectionModal(command_message_id=interaction.id)
        await interaction.response.send_modal(modal)

    async def purge_messages_from_timeframe(self, interaction: discord.Interaction):
        modal = TimeframeModal(command_message_id=interaction.id)
        await interaction.response.send_modal(modal)

class StopPurgeView(View):
    def __init__(self, parent_view):
        super().__init__(timeout=None)
        self.parent_view = parent_view

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.parent_view.stop_deletion = True
        button.disabled = True
        await interaction.response.edit_message(view=self)

class ConfirmPurgeAllView(View):
    def __init__(self, parent_view, command_message_id):
        super().__init__(timeout=None)
        self.parent_view = parent_view
        self.command_message_id = command_message_id

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger, custom_id="confirm_purge_all_unique")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.parent_view.perform_purge_with_stop(interaction, check_func=lambda m: m.id < self.command_message_id)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel_purge_all_unique")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Purge all messages canceled.", ephemeral=True)

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
            await self.view.purge_messages_from_user(interaction)
        elif option == "purge_timeframe":
            await self.view.purge_messages_from_timeframe(interaction)

class NumberInputModal(Modal, title="Purge number of messages"):
    def __init__(self, command_message_id):
        super().__init__()
        self.command_message_id = command_message_id

    number = TextInput(label="Number of messages to delete", placeholder="Enter a number (e.g., 10)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.number.value)
            if limit <= 0:
                raise ValueError("Number must be positive.")
            deleted_count = 0
            delay_between_deletions = 1.5
            status_view = StopPurgeView(self)
            status_message = await interaction.followup.send("Deleting messages...", view=status_view)
            async for message in interaction.channel.history(limit=limit):
                if getattr(self, "stop_deletion", False) or message.id >= self.command_message_id:
                    break
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
            final_text = f"Purge complete: Deleted {deleted_count} messages." if not getattr(self, "stop_deletion", False) else f"Purge stopped: {deleted_count} messages deleted."
            await status_message.edit(content=final_text, view=None)
        except ValueError:
            embed = create_embed("Error", "Please enter a valid positive integer.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

# Similar adjustments are made to UserSelectionModal and TimeframeModal to use command_message_id

async def setup(bot):
    await bot.add_cog(PurgeCog(bot))
