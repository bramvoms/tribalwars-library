import discord
from discord.ext import commands
import sqlite3
from main import create_embed  # Import the pre-configured embed function

class ReportToModsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("moderator_channels.db")
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS mod_channels (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)"
        )
        self.db.commit()

    def set_moderator_channel(self, guild_id: int, channel_id: int):
        """Set the moderator channel in the database."""
        self.cursor.execute(
            "INSERT OR REPLACE INTO mod_channels (guild_id, channel_id) VALUES (?, ?)",
            (guild_id, channel_id),
        )
        self.db.commit()

    def get_moderator_channel(self, guild_id: int):
        """Get the moderator channel ID for a guild from the database."""
        self.cursor.execute(
            "SELECT channel_id FROM mod_channels WHERE guild_id = ?", (guild_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    @commands.command(name="setmodchannel")
    @commands.has_permissions(administrator=True)
    async def set_mod_channel(self, ctx, channel: discord.TextChannel):
        """Sets the moderator channel for the current server. Only for administrators."""
        guild_id = ctx.guild.id
        self.set_moderator_channel(guild_id, channel.id)
        await ctx.send(f"Moderator channel set to {channel.mention}")

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
        
        # Retrieve the moderator channel from the database
        guild_id = interaction.guild.id
        mod_channel_id = self.get_moderator_channel(guild_id)
        if mod_channel_id:
            mod_channel = self.bot.get_channel(mod_channel_id)
            if mod_channel:
                # Send the embed publicly in the moderator's channel
                view = ReportView()
                await mod_channel.send(embed=embed, view=view)
            else:
                await interaction.followup.send("Moderator channel not found.", ephemeral=True)
        else:
            await interaction.followup.send("Moderator channel has not been set. Please contact an admin.", ephemeral=True)

class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout, button stays until manually removed

    @discord.ui.button(label="Resolved", style=discord.ButtonStyle.success)
    async def resolved_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Disable the button to prevent further clicks
        button.disabled = True

        # Safely retrieve the embed and update it
        if interaction.message.embeds:
            embed = interaction.message.embeds[0]
            embed.title = "✅ Resolved Report"
            embed.color = discord.Color.green()
            embed.add_field(name="Resolved by", value=interaction.user.mention, inline=False)
            embed.set_footer(text="This report has been marked as resolved by the moderation team.")

            # Edit the message in the channel with the updated embed and disabled button
            await interaction.message.edit(embed=embed, view=self)

            # Send an ephemeral confirmation message to the moderator
            await interaction.response.send_message("This report has been marked as resolved.", ephemeral=True)
        else:
            # Send an ephemeral message if no embed was found
            await interaction.response.send_message("No embed found to update.", ephemeral=True)
            
async def setup(bot):
    await bot.add_cog(ReportToModsCog(bot))
