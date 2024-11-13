import discord
from discord.ext import commands
from main import create_embed  # Import the pre-configured embed function

class ReportToModsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Replace with your server's specific moderator channel ID
        self.moderator_channel_id = 1241668734528258101  # Replace with actual channel ID

    async def report_message(self, interaction: discord.Interaction, message: discord.Message):
        # Send a private confirmation to the user who reported the message
        await interaction.response.send_message("Your report has been sent to the moderators.", ephemeral=True)

        # Prepare the title and description for the mod channel report message
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
        
        # Create a button view with the "Resolved" button for mods to mark the report as resolved
        view = ReportView()

        # Send the embed publicly in the moderators' channel
        mod_channel = self.bot.get_channel(self.moderator_channel_id)
        if mod_channel:
            await mod_channel.send(embed=embed, view=view)
        else:
            print("Moderator channel not found.")

class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout, button stays until manually removed

    @discord.ui.button(label="Resolved", style=discord.ButtonStyle.success)
    async def resolved_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Acknowledge the interaction to prevent "Interaction failed" messages
        await interaction.response.defer()

        # Disable the button after it's clicked to prevent further clicks
        button.disabled = True

        # Safely retrieve the embed, if present, and update it to indicate resolution
        if interaction.message.embeds:
            embed = interaction.message.embeds[0]
            embed.title = "✅ Report Resolved"
            embed.color = discord.Color.green()
            embed.set_footer(text="This report has been marked as resolved by the moderation team.")

            # Edit the message in the mod channel with the updated embed and disabled button
            await interaction.message.edit(embed=embed, view=self)
        else:
            print("No embed found on the message to update.")

async def setup(bot):
    await bot.add_cog(ReportToModsCog(bot))