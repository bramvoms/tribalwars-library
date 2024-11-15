import discord
from discord.ext import commands
from discord import app_commands
from main import create_embed
import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta
import os

class AutoModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        database_url = os.getenv("DATABASE_URL")
        self.db = psycopg2.connect(database_url, sslmode="require")
        self.cursor = self.db.cursor()

        # Create the table for forbidden words if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS forbidden_words (
                guild_id BIGINT,
                word TEXT,
                PRIMARY KEY (guild_id, word)
            );
        """)
        self.db.commit()

    def add_forbidden_word(self, guild_id: int, word: str):
        self.cursor.execute("""
            INSERT INTO forbidden_words (guild_id, word) VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (guild_id, word.lower()))
        self.db.commit()

    def remove_forbidden_word(self, guild_id: int, word: str):
        self.cursor.execute("""
            DELETE FROM forbidden_words WHERE guild_id = %s AND word = %s;
        """, (guild_id, word.lower()))
        self.db.commit()

    def get_forbidden_words(self, guild_id: int):
        self.cursor.execute("""
            SELECT word FROM forbidden_words WHERE guild_id = %s;
        """, (guild_id,))
        return [row[0] for row in self.cursor.fetchall()]

    @app_commands.command(name="add-automod", description="Add a forbidden word to Auto-Moderation.")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_automod(self, interaction: discord.Interaction, word: str):
        guild_id = interaction.guild_id
        self.add_forbidden_word(guild_id, word)
        await interaction.response.send_message(f"Added forbidden word: `{word}`", ephemeral=True)

    @app_commands.command(name="remove-automod", description="Remove a forbidden word from Auto-Moderation.")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_automod(self, interaction: discord.Interaction, word: str):
        guild_id = interaction.guild_id
        self.remove_forbidden_word(guild_id, word)
        await interaction.response.send_message(f"Removed forbidden word: `{word}`", ephemeral=True)

    @app_commands.command(name="view-automod", description="View the list of forbidden words.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def view_automod(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        forbidden_words = self.get_forbidden_words(guild_id)
        if forbidden_words:
            words_list = "\n".join(f"`{word}`" for word in forbidden_words)
            embed = create_embed(
                title="Forbidden Words",
                description=f"**Current forbidden words in this server:**\n{words_list}"
            )
        else:
            embed = create_embed(
                title="Forbidden Words",
                description="No forbidden words have been added yet."
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        forbidden_words = self.get_forbidden_words(guild_id)

        # Check if the message contains any forbidden words
        bad_words = [word for word in forbidden_words if word in message.content.lower()]
        if bad_words:
            await message.delete()  # Delete the message

            # Generate nickname or display name for warning
            nickname_or_displayname = message.author.nick or message.author.display_name
            embed = create_embed(
                title=f"{nickname_or_displayname} has been warned",
                description=(
                    f"**Reason:** Bad word usage\n"
                    f"**Message content:**\n{message.content}\n\n"
                )
            )
            await message.channel.send(embed=embed)

            # Apply warning and timeout logic
            current_time = datetime.utcnow()
            self.cursor.execute("""
                INSERT INTO warnings (user_id, guild_id, timestamp, moderator_id)
                VALUES (%s, %s, %s, %s);
            """, (message.author.id, guild_id, current_time, self.bot.user.id))
            self.db.commit()

            # Count warnings in the last 20 minutes
            self.cursor.execute("""
                SELECT COUNT(*) FROM warnings
                WHERE user_id = %s AND guild_id = %s AND timestamp > %s;
            """, (message.author.id, guild_id, current_time - timedelta(minutes=20)))
            warnings_count = self.cursor.fetchone()[0]

            if warnings_count >= 3:
                timeout_duration = timedelta(minutes=60)
                try:
                    await message.author.timeout(timeout_duration, reason="Auto-Mod: 3 warnings within 20 minutes.")
                    embed = create_embed(
                        title=f"{nickname_or_displayname}, you have been timed-out.",
                        description=(
                            f"**Reason:** Repeated bad word usage.\n"
                            f"**Duration:** 60 minutes.\n"
                        )
                    )
                    await message.channel.send(embed=embed)
                except discord.Forbidden:
                    await message.channel.send("Unable to timeout the user due to insufficient permissions.")

async def setup(bot):
    await bot.add_cog(AutoModCog(bot))
