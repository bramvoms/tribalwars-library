import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button
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
        stop_deletion = False

        # Create a status message with a 'Stop' button
        status_view = StopPurgeView()
        status_view.set_stop_flag(lambda: setattr(self, "stop_deletion", True))
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

class StopPurgeView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.stop_flag = None

    def set_stop_flag(self, stop_func):
        """Set the function to call when the stop button is pressed."""
        self.stop_flag = stop_func

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Stop the purge and disable the button
        if self.stop_flag:
            self.stop_flag()
        button.disabled = True
        await interaction.response.edit_message(view=self)

class ConfirmPurgeAllView(View):
    def __init__(self, parent_view):
        super().__init__(timeout=None)
        self.parent_view = parent_view

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger, custom_id="confirm_purge_all_unique")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parent_view.perform_purge_with_stop(interaction, check_func=lambda _: True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel_purge_all_unique")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Purge all messages canceled.", ephemeral=True)

class PurgeOptionsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Purge all messages", value="purge_all", description="Delete all messages in the channel."),
            discord.SelectOption(label="Purge non-bot messages", value="purge_non_bot", description="Delete all messages sent by users."),
            discord.SelectOption(label="Purge bot messages", value="purge_bot", description="Delete all messages sent by bots."),
        ]
        super().__init__(placeholder="Select a purge option...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        option = self.values[0]
        if option == "purge_all":
            await self.view.purge_all_messages(interaction)
        elif option == "purge_non_bot":
            await self.view.purge_non_bot_messages(interaction)
        elif option == "purge_bot":
            await self.view.purge_bot_messages(interaction)

async def setup(bot):
    await bot.add_cog(PurgeCog(bot))
