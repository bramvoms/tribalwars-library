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
        view = ConfirmPurgeAllView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def perform_purge_with_stop(self, interaction: discord.Interaction, check_func):
        """Perform the purge with a 'Stop' button to allow the user to halt purging."""
        total_deleted = 0
        delay_between_deletions = 1.5

        # Create a status message with a 'Stop' button
        status_view = StopPurgeView(self)
        status_message = await interaction.followup.send("Deleting messages...", view=status_view)

        async for message in interaction.channel.history(limit=None):
            if self.stop_deletion:
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

        # Update the status message with the deletion summary
        final_text = f"Purge complete: Deleted {total_deleted} messages." if not self.stop_deletion else f"Purge stopped: {total_deleted} messages deleted."
        await status_message.edit(content=final_text, view=None)

    async def purge_non_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.perform_purge_with_stop(interaction, check_func=lambda m: not m.author.bot)

    async def purge_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.perform_purge_with_stop(interaction, check_func=lambda m: m.author.bot)

    async def prompt_number_of_messages(self, interaction: discord.Interaction):
        modal = NumberInputModal()
        await interaction.response.send_modal(modal)

    async def purge_messages_from_user(self, interaction: discord.Interaction):
        modal = UserSelectionModal()
        await interaction.response.send_modal(modal)

    async def purge_messages_from_timeframe(self, interaction: discord.Interaction):
        modal = TimeframeModal()
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
    def __init__(self, parent_view):
        super().__init__(timeout=None)
        self.parent_view = parent_view

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger, custom_id="confirm_purge_all_unique")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Defer the interaction to prevent webhook errors
        await interaction.response.defer()
        # Perform the purge with a stop button
        await self.parent_view.perform_purge_with_stop(interaction, check_func=lambda _: True)

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
    number = TextInput(label="Number of messages to delete", placeholder="Enter a number (e.g., 10)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.number.value)
            if limit <= 0:
                raise ValueError("Number must be positive.")
            
            # Defer the interaction response to avoid webhook errors
            await interaction.response.defer(thinking=True)
            
            deleted_count = 0
            delay_between_deletions = 1.5
            status_view = StopPurgeView(self)  # Assuming StopPurgeView is defined with stop functionality
            status_message = await interaction.followup.send("Deleting messages...", view=status_view)
            
            async for message in interaction.channel.history(limit=limit):
                if getattr(self, "stop_deletion", False):
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

class UserSelectionModal(Modal, title="Purge messages from a User"):
    user_input = TextInput(label="User ID or mention", placeholder="Enter the user's ID or mention them", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = int(self.user_input.value.strip("<@!>")) if self.user_input.value.isdigit() else None
        if not user_id:
            await interaction.response.send_message("Invalid user ID or mention.", ephemeral=True)
            return
        await PurgeOptionsView().perform_purge_with_stop(interaction, check_func=lambda m: m.author.id == user_id)

class TimeframeModal(Modal, title="Purge Messages from a Timeframe"):
    hours = TextInput(label="Hours", placeholder="Enter the number of hours", required=False)
    minutes = TextInput(label="Minutes", placeholder="Enter the number of minutes", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        hours = int(self.hours.value) if self.hours.value else 0
        minutes = int(self.minutes.value) if self.minutes.value else 0
        if hours == 0 and minutes == 0:
            await interaction.response.send_message("Please enter a valid timeframe.", ephemeral=True)
            return
        from datetime import datetime, timedelta
        time_limit = datetime.utcnow() - timedelta(hours=hours, minutes=minutes)
        await PurgeOptionsView().perform_purge_with_stop(interaction, check_func=lambda m: m.created_at >= time_limit)

async def setup(bot):
    await bot.add_cog(PurgeCog(bot))
