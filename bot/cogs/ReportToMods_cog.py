import discord
from discord.ext import commands
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2 import sql
from main import create_embed

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
                timestamp TIMESTAMP
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

        embed = create_embed(title=title, description=description)
        embed.set_footer(text="Use this information for appropriate moderation actions.")
        
        guild_id = interaction.guild.id
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
            embed.title = "✅ Resolved Report"
            embed.color = discord.Color.green()
            embed.add_field(name="Resolved by", value=interaction.user.mention, inline=False)
            embed.set_footer(text="This report has been marked as resolved by the moderation team.")
            await interaction.message.edit(embed=embed, view=self)
            await interaction.response.send_message("This report has been marked as resolved.", ephemeral=True)

    async def send_violation_dm(self, member, message, reason):
        """Sends a DM to the user with details of their message violation."""
        title = "Message Violation Notice"
        description = (
            f"Your message in **{message.guild.name}** (#{message.channel.name}) was removed for violating server rules.\n\n"
            f"**Message Content:**\n{message.content}\n\n"
            f"**Action Taken:** {reason}"
        )
        embed = create_embed(title=title, description=description)
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

    @discord.ui.button(label="Warn Author", style=discord.ButtonStyle.primary)
    async def warn_author_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.warn_author(interaction)
        await self.mark_as_resolved(interaction)

    async def warn_author(self, interaction: discord.Interaction):
        author = self.message.author
        guild_id = interaction.guild.id
        current_time = datetime.utcnow()

        # Insert the new warning into the database
        self.bot.get_cog("ReportToModsCog").cursor.execute(
            "INSERT INTO warnings (user_id, guild_id, timestamp) VALUES (%s, %s, %s)",
            (author.id, guild_id, current_time)
        )
        self.bot.get_cog("ReportToModsCog").db.commit()

        # Retrieve warnings in the last 8 hours
        self.bot.get_cog("ReportToModsCog").cursor.execute(
            """
            SELECT COUNT(*) FROM warnings
            WHERE user_id = %s AND guild_id = %s AND timestamp > %s
            """,
            (author.id, guild_id, current_time - timedelta(hours=8))
        )
        warning_count = self.bot.get_cog("ReportToModsCog").cursor.fetchone()[0]

        if warning_count >= 3:
            # Timeout the user for 1 day
            try:
                await author.timeout_for(timedelta(days=1), reason="Accumulated 3 warnings in 8 hours.")
                dm_message = (
                    f"You have been timed out for 1 day in **{interaction.guild.name}** due to multiple violations. "
                    f"Your message in {self.message.channel.mention} was: \n\n{self.message.content}"
                )
            except discord.Forbidden:
                await interaction.response.send_message("Unable to timeout the user due to permission issues.", ephemeral=True)
                return
        else:
            dm_message = (
                f"You have received a warning in **{interaction.guild.name}**. "
                f"Your message in {self.message.channel.mention} was: \n\n{self.message.content}"
            )

        # Send DM to the user
        try:
            embed = create_embed(
                title="⚠️ Warning Notification",
                description=dm_message
            )
            await author.send(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("Unable to send a DM to the user.", ephemeral=True)

        # Delete the original message
        await self.message.delete()
        await interaction.response.send_message("Author warned and message deleted.", ephemeral=True)

    @discord.ui.button(label="Resolved", style=discord.ButtonStyle.success)
    async def resolved_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.mark_as_resolved(interaction)
        await interaction.response.send_message("This report has been marked as resolved.", ephemeral=True)

    @discord.ui.button(label="Delete Message", style=discord.ButtonStyle.danger)
    async def delete_message_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_violation_dm(self.message.author, self.message, "Message Deleted")
        await self.message.delete()
        await self.mark_as_resolved(interaction)
        await interaction.response.send_message("Message deleted, author notified, and report marked as resolved.", ephemeral=True)

    @discord.ui.button(label="Time-Out Options", style=discord.ButtonStyle.danger)
    async def timeout_options_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.mark_as_resolved(interaction)
        await interaction.response.send_message(
            "Select a time-out duration for the user:", 
            view=TimeoutDurationView(self.message.author, self.message),
            ephemeral=True
        )

    @discord.ui.button(label="Ban Author", style=discord.ButtonStyle.danger)
    async def ban_author_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_violation_dm(self.message.author, self.message, "Permanent Ban")
        await self.message.author.ban(reason="Violation of server rules")
        await self.message.delete()
        await self.mark_as_resolved(interaction)
        await interaction.response.send_message("Author banned, notified, and report marked as resolved.", ephemeral=True)

class TimeoutDurationView(discord.ui.View):
    def __init__(self, member, message):
        super().__init__(timeout=None)
        self.member = member
        self.message = message

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

    async def apply_timeout(self, interaction: discord.Interaction, duration: timedelta):
        try:
            await ReportView.send_violation_dm(self, self.member, self.message, f"Timed Out for {duration}")
            await self.member.timeout(duration, reason="Violation of server rules.")
            await self.message.delete()
            await interaction.response.send_message(f"{self.member.mention} has been timed out for {duration}, message deleted, and author notified.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Unable to time out the user or delete the message due to permission issues.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ReportToModsCog(bot))
