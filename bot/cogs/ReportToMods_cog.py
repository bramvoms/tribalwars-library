import discord
from discord.ext import commands
from discord import app_commands, Interaction
from main import create_embed  # Import the pre-configured embed function

class ReportToModsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Replace with your server's specific moderator channel ID
        self.moderator_channel_id = 1241668734528258101  # Replace with actual channel ID

        # Create a command tree instance for context menus
        self.tree = app_commands.CommandTree(self.bot)

    async def cog_load(self):
        # Register the context menu command on cog load
        self.tree.add_command(app_commands.ContextMenu(
            name="Report to Mods",
            callback=self.report_message
        ))
        await self.tree.sync()  # Sync commands with Discord

    async def report_message(self, interaction: discord.Interaction, message: discord.Message):
        mod_channel = self.bot.get_channel(self.moderator_channel_id)
        
        if mod_channel is None:
            await interaction.response.send_message("Moderator channel not found. Please contact an admin.", ephemeral=True)
            return

        # Prepare the title and description using your preferred embed style
        title = "⚠️ New Message Report"
        description = (
            f"**Reported Message**: {message.content}\n\n"
            f"**Reported by**: {interaction.user.mention}\n"
            f"**Author**: {message.author.mention}\n"
            f"**Channel**: {message.channel.mention}\n"
            f"[Jump to Message]({message.jump_url})"
        )

        # Use create_embed from main.py for consistent embed styling
        embed = create_embed(title=title, description=description)
        embed.set_footer(text="Use this information for appropriate moderation actions.")

        # Create a button view for the "Resolved" button
        view = ReportView()

        # Send the embed to the moderators' channel with the "Resolved" button
        await mod_channel.send(embed=embed, view=view)
        await interaction.response.send_message("Your report has been sent to the moderators.", ephemeral=True)

class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout, button stays until manually removed

    @discord.ui.button(label="Resolved", style=discord.ButtonStyle.success)
    async def resolved_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Disable the button after it's clicked to prevent multiple resolutions
        button.disabled = True
        # Update the original message to indicate the report has been resolved
        embed = interaction.message.embeds[0]
        embed.title = "✅ Report Resolved"
        embed.color = discord.Color.green()
        embed.set_footer(text="This report has been marked as resolved.")
        
        # Edit the message with the updated embed and disabled button
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("This report has been marked as resolved.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ReportToModsCog(bot))
