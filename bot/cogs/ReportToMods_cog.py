import discord
from discord.ext import commands
from discord import app_commands, Interaction
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2 import sql
from main import create_embed
import logging
import sys

# Set up logging for Heroku
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class ReportToModsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        database_url = os.getenv("DATABASE_URL")
        self.db = psycopg2.connect(database_url, sslmode="require")
        self.cursor = self.db.cursor()

        # Create the tables if they don't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mod_channels (
                guild_id BIGINT PRIMARY KEY,
                channel_id BIGINT
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                user_id BIGINT,
                guild_id BIGINT,
                timestamp TIMESTAMP,
                moderator_id BIGINT
            );
        """)
        self.db.commit()

    def set_moderator_channel(self, guild_id: int, channel_id: int):
        self.cursor.execute(
            sql.SQL("INSERT INTO mod_channels (guild_id, channel_id) VALUES (%s, %s) ON CONFLICT (guild_id) DO UPDATE SET channel_id = EXCLUDED.channel_id"),
            (guild_id, channel_id)
        )
        self.db.commit()

    def get_moderator_channel(self, guild_id: int):
        self.cursor.execute(
            sql.SQL("SELECT channel_id FROM mod_channels WHERE guild_id = %s"),
            (guild_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    @commands.command(name="setmodchannel")
    @commands.has_permissions(administrator=True)
    async def set_mod_channel(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        self.set_moderator_channel(guild_id, channel.id)
        await ctx.send(f"Moderator channel set to {channel.mention}")

        async def report_message(self, interaction: discord.Interaction, message: discord.Message):
            await interaction.response.send_message("Your report has been sent to the moderators.", ephemeral=True)

            title = "⚠️ New Message Report!"
            description = (
                f"**Reported Message**: \n{message.content}\n\n"
                f"**Reported by**: {interaction.user.mention}\n"
                f"**Author**: {message.author.mention}\n"
                f"**Channel**: {message.channel.mention}\n"
                f"[Jump to Message]({message.jump_url})"
            )

            # Fetch warning information for the author in the last 8 hours
            guild_id = interaction.guild.id
            current_time = datetime.utcnow()
            self.cursor.execute(
                """
                SELECT warning_id, moderator_id, timestamp
                FROM warnings
                WHERE user_id = %s AND guild_id = %s AND timestamp > %s
                ORDER BY warning_id ASC
                """,
                (message.author.id, guild_id, current_time - timedelta(hours=8))
            )
            results = self.cursor.fetchall()

            # Build warning info with inline format for table-like display
            warning_info = f"{len(results)} warning(s) in the last 8 hours.\n"
            warning_info += "Warning # | Timestamp | Moderator\n"
            warning_info += "-----------|----------------|------------\n"

            for warning_id, mod_id, timestamp in results:
                mod_member = interaction.guild.get_member(mod_id)
                mod_name = mod_member.display_name if mod_member else f"Moderator ID: {mod_id}"
                formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                warning_info += f"{warning_id} | {formatted_timestamp} | {mod_name}\n"

            # Add warning information to the embed
            embed = create_embed(title=title, description=description)
            embed.add_field(name="Previous Warnings", value=warning_info, inline=False)
            embed.set_footer(text="Use this information for appropriate moderation actions.")

            mod_channel_id = self.get_moderator_channel(guild_id)
            if mod_channel_id:
                mod_channel = self.bot.get_channel(mod_channel_id)
                if mod_channel:
                    view = ReportView(message, self.bot)
                    await mod_channel.send(embed=embed, view=view)
                else:
                    await interaction.followup.send("Moderator channel not found.", ephemeral=True)
            else:
                await interaction.followup.send("Moderator channel has not been set. Please contact an admin.", ephemeral=True)

    @app_commands.command(name="removewarnings", description="Remove warnings for a specified user.")
    @app_commands.describe(user="The user to remove warnings from within this guild.", all="Remove all warnings? (Y/N)", timeframe="If 'N', specify timeframe in hours")
    @app_commands.checks.has_permissions(administrator=True)
    async def removewarnings(self, interaction: discord.Interaction, user: discord.User, all: str, timeframe: int = 0):
        guild_id = interaction.guild.id

        # Verify that the specified user exists in the guild
        guild_member = interaction.guild.get_member(user.id)
        if not guild_member:
            await interaction.response.send_message("The specified user is not a member of this guild.", ephemeral=True)
            return

        try:
            if all.upper() == 'Y':
                # Remove all warnings for the user in this guild
                self.cursor.execute(
                    "DELETE FROM warnings WHERE user_id = %s AND guild_id = %s",
                    (user.id, guild_id)
                )
                self.db.commit()
                await interaction.response.send_message(f"All warnings for {guild_member.display_name} have been removed.", ephemeral=True)
            else:
                # Remove warnings within a specified timeframe
                timeframe_delta = datetime.utcnow() - timedelta(hours=timeframe)
                self.cursor.execute(
                    "DELETE FROM warnings WHERE user_id = %s AND guild_id = %s AND timestamp > %s",
                    (user.id, guild_id, timeframe_delta)
                )
                self.db.commit()
                await interaction.response.send_message(f"Warnings for {guild_member.display_name} within the last {timeframe} hours have been removed.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while removing warnings: {str(e)}", ephemeral=True)
            
    def set_moderator_channel(self, guild_id: int, channel_id: int):
        self.cursor.execute(
            sql.SQL("INSERT INTO mod_channels (guild_id, channel_id) VALUES (%s, %s) ON CONFLICT (guild_id) DO UPDATE SET channel_id = EXCLUDED.channel_id"),
            (guild_id, channel_id)
        )
        self.db.commit()

    def get_moderator_channel(self, guild_id: int):
        self.cursor.execute(
            sql.SQL("SELECT channel_id FROM mod_channels WHERE guild_id = %s"),
            (guild_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    @commands.command(name="setmodchannel")
    @commands.has_permissions(administrator=True)
    async def set_mod_channel(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        self.set_moderator_channel(guild_id, channel.id)
        await ctx.send(f"Moderator channel set to {channel.mention}")

    async def report_message(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_message("Your report has been sent to the moderators.", ephemeral=True)

        title = "⚠️ New Message Report!"
        description = (
            f"**Reported Message**: \n{message.content}\n\n"
            f"**Reported by**: {interaction.user.mention}\n"
            f"**Author**: {message.author.mention}\n"
            f"**Channel**: {message.channel.mention}\n"
            f"[Jump to Message]({message.jump_url})"
        )

        # Fetch warning information for the author in the last 8 hours
        guild_id = interaction.guild.id
        current_time = datetime.utcnow()
        self.cursor.execute(
            """
            SELECT COUNT(*), array_agg(DISTINCT moderator_id), array_agg(DISTINCT timestamp)
            FROM warnings
            WHERE user_id = %s AND guild_id = %s AND timestamp > %s
            """,
            (message.author.id, guild_id, current_time - timedelta(hours=8))
        )
        result = self.cursor.fetchone()
        warning_count = result[0]
        moderator_ids = result[1] if result[1] else []
        timestamps = result[2] if result[2] else []

        # Build the moderator warning information for the report message
        warning_info = f"{warning_count} warning(s) in the last 8 hours.\n"
        for mod_id, timestamp in zip(moderator_ids, timestamps):
            mod_member = interaction.guild.get_member(mod_id)
            mod_name = mod_member.display_name if mod_member else f"Moderator ID: {mod_id}"
            warning_info += f"- {mod_name} at {timestamp}\n"

        # Add warning information to the embed
        embed = create_embed(title=title, description=description)
        embed.add_field(name="Previous warnings", value=warning_info, inline=False)
        embed.set_footer(text="Use this information for appropriate moderation actions.")

        mod_channel_id = self.get_moderator_channel(guild_id)
        if mod_channel_id:
            mod_channel = self.bot.get_channel(mod_channel_id)
            if mod_channel:
                view = ReportView(message, self.bot)
                await mod_channel.send(embed=embed, view=view)
            else:
                await interaction.followup.send("Moderator channel not found.", ephemeral=True)
        else:
            await interaction.followup.send("Moderator channel has not been set. Please contact an admin.", ephemeral=True)

class ReportView(discord.ui.View):
    def __init__(self, message, bot):
        super().__init__(timeout=None)
        self.message = message
        self.bot = bot

    async def mark_as_resolved(self, interaction):
        for item in self.children:
            item.disabled = True
        if interaction.message.embeds:
            embed = interaction.message.embeds[0]
            embed.title = "✅ Resolved report"
            embed.color = discord.Color.green()
            embed.add_field(name="Resolved by", value=interaction.user.mention, inline=False)
            embed.set_footer(text="This report has been marked as resolved by the moderation team.")
            await interaction.message.edit(embed=embed, view=self)
        
        # Avoid sending a second response if already responded
        if not interaction.response.is_done():
            await interaction.response.send_message("This report has been marked as resolved.", ephemeral=True)

    async def send_violation_dm(self, member, message, reason):
        """Sends a DM to the user with details of their message violation."""
        title = "Moderator message"
        description = (
            f"Your message in {self.message.channel.mention} was removed for violating server rules.\n\n"
            f"**Message Content:**\n{message.content}\n\n"
            f"**Action Taken:** \n{reason}"
        )
        embed = create_embed(title=title, description=description)
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

    @discord.ui.button(label="Delete message", style=discord.ButtonStyle.danger)
    async def delete_message_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_violation_dm(self.message.author, self.message, "Message deleted")
        await self.message.delete()
        await self.mark_as_resolved(interaction)

    @discord.ui.button(label="Warn author", style=discord.ButtonStyle.danger)
    async def warn_author_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.warn_author(interaction)
        await self.mark_as_resolved(interaction)

    async def warn_author(self, interaction: discord.Interaction):
        author = self.message.author
        guild_id = interaction.guild.id
        current_time = datetime.utcnow().replace(microsecond=0)  # Remove milliseconds

        # Add warning to the database
        self.bot.get_cog("ReportToModsCog").cursor.execute(
            "INSERT INTO warnings (user_id, guild_id, timestamp, moderator_id) VALUES (%s, %s, %s, %s)",
            (author.id, guild_id, current_time, interaction.user.id)
        )
        self.bot.get_cog("ReportToModsCog").db.commit()

        # Count warnings in the last 8 hours
        self.bot.get_cog("ReportToModsCog").cursor.execute(
            """
            SELECT COUNT(*) FROM warnings
            WHERE user_id = %s AND guild_id = %s AND timestamp > %s
            """,
            (author.id, guild_id, current_time - timedelta(hours=8))
        )
        warning_count = self.bot.get_cog("ReportToModsCog").cursor.fetchone()[0]

        if warning_count >= 3:
            try:
                await author.timeout(timedelta(days=1), reason="Accumulated 3 warnings in 8 hours.")
                dm_message = (
                    f"You have been timed out for 1 day in **{interaction.guild.name}** due to multiple violations. "
                    f"Your message in {self.message.channel.mention} was: \n\n{self.message.content}"
                )
            except discord.Forbidden:
                await interaction.response.send_message("Unable to timeout the user due to permission issues.", ephemeral=True)
                return
        else:
            dm_message = (
                f"You have received a warning in **{interaction.guild.name}** for violating server rules. If you accumulate three warnings within 8 hours, you will get timed-out."
                f"Your message in {self.message.channel.mention} was: \n\n{self.message.content}"
            )

        # Send DM to the user
        try:
            embed = create_embed(
                title="Moderator message",
                description=dm_message
            )
            await author.send(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("Unable to send a DM to the user.", ephemeral=True)

        # Delete the original message
        await self.message.delete()
        if not interaction.response.is_done():
            await interaction.response.send_message("Author warned and message deleted.", ephemeral=True)

    @discord.ui.button(label="Time-out author", style=discord.ButtonStyle.danger)
    async def timeout_options_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.mark_as_resolved(interaction)
        view = TimeoutDurationView(self.message.author, self.message, self)
        await interaction.message.edit(content="Select a time-out duration for the user:", view=view)

    @discord.ui.button(label="Ban author", style=discord.ButtonStyle.danger)
    async def ban_author_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_violation_dm(self.message.author, self.message, "Permanent ban")
        await self.message.author.ban(reason="Violation of server rules")
        await self.message.delete()
        await self.mark_as_resolved(interaction)

    @discord.ui.button(label="No further action", style=discord.ButtonStyle.success)
    async def resolved_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.mark_as_resolved(interaction)

class TimeoutDurationView(discord.ui.View):
    def __init__(self, member, message, report_view):
        super().__init__(timeout=None)
        self.member = member
        self.message = message
        self.report_view = report_view  # Store reference to ReportView

    async def apply_timeout(self, interaction: discord.Interaction, duration: timedelta):
        try:
            await self.report_view.send_violation_dm(self.member, self.message, f"Timed out for {duration}")
            await self.member.timeout(duration, reason="Violation of server rules.")
            await self.message.delete()
            await interaction.response.send_message(
                f"{self.member.mention} has been timed out for {duration}, message deleted, and author notified.",
                ephemeral=True
            )
            # Mark the report as resolved after the time-out duration is applied
            await self.report_view.mark_as_resolved(interaction)
        except discord.Forbidden:
            await interaction.response.send_message("Unable to time out the user or delete the message due to permission issues.", ephemeral=True)

    @discord.ui.button(label="1 Minute", style=discord.ButtonStyle.secondary)
    async def timeout_1_minute(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_timeout(interaction, timedelta(minutes=1))

    @discord.ui.button(label="5 Minutes", style=discord.ButtonStyle.secondary)
    async def timeout_5_minutes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_timeout(interaction, timedelta(minutes=5))

    @discord.ui.button(label="10 Minutes", style=discord.ButtonStyle.secondary)
    async def timeout_10_minutes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_timeout(interaction, timedelta(minutes=10))

    @discord.ui.button(label="1 Hour", style=discord.ButtonStyle.secondary)
    async def timeout_1_hour(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_timeout(interaction, timedelta(hours=1))

    @discord.ui.button(label="1 Day", style=discord.ButtonStyle.secondary)
    async def timeout_1_day(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_timeout(interaction, timedelta(days=1))

    @discord.ui.button(label="1 Week", style=discord.ButtonStyle.secondary)
    async def timeout_1_week(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_timeout(interaction, timedelta(weeks=1))

async def setup(bot):
    await bot.add_cog(ReportToModsCog(bot))
