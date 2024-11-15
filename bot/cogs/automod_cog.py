import discord
from discord.ext import commands
from discord import app_commands, Interaction
from datetime import datetime, timedelta
from collections import defaultdict
from main import create_embed


class AutoModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.forbidden_words = set()  # Store forbidden words
        self.warned_users = defaultdict(list)  # Track warnings with timestamps

    # Add a word to the forbidden list
    @app_commands.command(name="add-automod", description="Add a forbidden word to the auto-moderation list.")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_automod(self, interaction: Interaction, word: str):
        self.forbidden_words.add(word.lower())
        embed = create_embed(
            title="✅ Auto-Mod Update",
            description=f"`{word}` has been added to the forbidden words list."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Remove a word from the forbidden list
    @app_commands.command(name="remove-automod", description="Remove a forbidden word from the auto-moderation list.")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_automod(self, interaction: Interaction, word: str):
        if word.lower() in self.forbidden_words:
            self.forbidden_words.remove(word.lower())
            embed = create_embed(
                title="✅ Auto-Mod Update",
                description=f"`{word}` has been removed from the forbidden words list."
            )
        else:
            embed = create_embed(
                title="⚠️ Word Not Found",
                description=f"`{word}` is not in the forbidden words list."
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # View all forbidden words
    @app_commands.command(name="view-automod", description="View the forbidden words in the auto-moderation list.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def view_automod(self, interaction: Interaction):
        if not self.forbidden_words:
            description = "There are currently no forbidden words in the auto-moderation list."
        else:
            words_list = ", ".join(sorted(self.forbidden_words))
            description = f"**Forbidden Words:**\n{words_list}"

        embed = create_embed(
            title="📜 Auto-Mod Forbidden Words",
            description=description
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Check messages for forbidden words
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:  # Ignore bot messages or DMs
            return

        # Check for forbidden words
        words_in_message = message.content.lower().split()
        bad_words = [word for word in words_in_message if word in self.forbidden_words]

        if bad_words:
            await message.delete()  # Delete the message
            embed = create_embed(
                # Generate title using server nickname or display name
                nickname_or_displayname = message.author.nick or message.author.display_name
                title = f"{nickname_or_displayname} has been warned",
                description=f"**Reason:** Bad word usage"
            )
            await message.channel.send(embed=embed)

            now = datetime.utcnow()
            self.warned_users[message.author.id].append(now)

            # Filter warnings older than 20 minutes
            recent_warnings = [
                warn_time for warn_time in self.warned_users[message.author.id]
                if now - warn_time <= timedelta(minutes=20)
            ]
            self.warned_users[message.author.id] = recent_warnings

            # Apply timeout if warnings reach 3 within 20 minutes
            if len(recent_warnings) >= 3:
                await self.timeout_user(message.author, message)

    async def timeout_user(self, member: discord.Member, message: discord.Message):
        """Timeout a user for 60 minutes and notify them."""
        timeout_duration = timedelta(minutes=60)
        try:
            # Apply timeout
            await member.timeout(timeout_duration, reason="Auto-Mod: 3 warnings within 20 minutes.")
            embed = create_embed(
                # Generate title using server nickname or display name
                nickname_or_displayname = message.author.nick or message.author.display_name
                title = f"{nickname_or_displayname}, you have been timed-out.",
                description=(
                    f"**Reason:** Repeated bad word usage.\n"
                    f"**Duration:** 60 minutes.\n"
                )
            )
            await message.channel.send(embed=embed)

            # Notify user via DM
            dm_embed = create_embed(
                title="⚠️ Auto-Moderation Warning",
                description=(
                    f"You have been timed out in **{message.guild.name}** for 60 minutes due to repeated rule violations.\n\n"
                    f"**Reason:** Bad word usage.\n"
                    f"**Message content:**\n{message.content}"
                )
            )
            try:
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # Ignore if DMs are disabled
        except discord.Forbidden:
            await message.channel.send(
                f"⚠️ I do not have permission to time out {member.mention}. Please check my role permissions."
            )


async def setup(bot):
    await bot.add_cog(AutoModCog(bot))
