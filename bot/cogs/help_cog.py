import discord
from discord.ext import commands
from main import create_embed

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bothelp", help="Displays all available bot commands with their descriptions.")
    async def help_command(self, ctx):
        # Create an embed for the help menu
        embed = create_embed(
            title=f"━━━━━━ TribalWars Library ━━━━━━",
            description="Here is a list of all available commands and their descriptions. Use them to navigate and utilize bot functionalities."
        )

        # Add a short description for each command
        embed.add_field(
            name="`/scripts`",
            value="Displays a categorized menu for all available scripts. You can browse or search for specific scripts.",
            inline=False
        )

        embed.add_field(
            name="`&scripts <script_name>`",
            value="Search for a script by name. Provides the closest matching script if an exact match isn't found.",
            inline=False
        )

        embed.add_field(
            name="`/am`",
            value="Displays a menu for AM (Automated Management) templates and options. Browse templates and view details.",
            inline=False
        )

        embed.add_field(
            name="`&am <template_name>`",
            value="Search for an AM template by name. Provides the closest matching template if an exact match isn't found.",
            inline=False
        )

        embed.add_field(
            name="`/purge`",
            value="Opens a menu for purging messages in a channel with multiple options, including number of messages and specific users.",
            inline=False
        )

        embed.add_field(
            name="`&help`",
            value="Show all bot functionalities",
            inline=False
        )

        embed.set_footer(text="Use commands with prefixes '&' or '/' as specified\nTribalWars Library - Created by Victorious")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
