import discord
from discord.ext import commands
from main import create_embed  # Import create_embed from main.py

class WelcomeMessageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Get the welcome and rules channels from the server settings
        guild = member.guild
        welcome_channel = guild.system_channel  # This gets the server's system channel
        rules_channel = guild.rules_channel  # This gets the server's rules channel (if configured)

        # Use server nickname if set, otherwise fallback to display_name
        display_name = member.nick if member.nick else member.display_name

        rules_channel_mention = f"<#{rules_channel.id}>" if rules_channel else "the rules channel"

        if welcome_channel:
            # Create the public welcome message
            embed = create_embed(
                title=f"WELCOME {display_name}",
                description=(
                    f"{member.mention} has joined **{guild.name}**!\n\n"
                    f"**Rules & information**\n"
                    f"Please make sure to check {rules_channel_mention} for the rules of the server.\n"
                    f"Use <id:customize> to browse channels.\n\n"
                    f"Have fun!"
                )
            )
            embed.set_thumbnail(url=member.display_avatar.url)  # User's profile picture
            embed.set_footer(
                text=f"{discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\nTribalWars Library - Created by Victorious",
                icon_url="https://i.imgur.com/N6Z8wxx.png"  # Footer icon from main.py
            )
            await welcome_channel.send(embed=embed)

        # Send a DM to the new member
        try:
            dm_embed = create_embed(
                title=f"WELCOME {display_name}",
                description=(
                    f"Welcome to **{guild.name}**, {member.mention}!\n\n"
                    f"Please make sure to check {rules_channel_mention} for the rules of the server.\n"
                    f"Use Channels & Roles to browse channels.\n\n"
                    f"Have fun!"
                )
            )
            dm_embed.set_thumbnail(url="https://i.imgur.com/GDJE1uD.png")  # Thumbnail from main.py
            dm_embed.set_footer(
                text="TribalWars Library - Created by Victorious",
                icon_url="https://i.imgur.com/N6Z8wxx.png"  # Footer icon from main.py
            )
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            # Handle cases where the user has disabled DMs from server members
            print(f"Could not send a DM to {display_name} ({member.mention}).")

async def setup(bot):
    await bot.add_cog(WelcomeMessageCog(bot))
