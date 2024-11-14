import discord
from discord.ext import commands
from main import create_embed

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bothelp", help="Shows all available commands for the TribalWars Library bot.")
    async def help_command(self, ctx):
        # Create an embed for the help menu
        embed = create_embed(
            title=f"━ TribalWars Library ━",
            description="This bot provides a range of commands and functionalities to enhance your experience. Below is a list of all available commands and features."
        )

        # Add a short description for each command
        embed.add_field(
            name="`/scripts`",
            value="Displays a interactive menu to browse through all approved scripts. Select a category or search directly in the full database. WARNING: TribalWars.nl ONLY.",
            inline=False
        )

        embed.add_field(
            name="`&scripts <script_name>`",
            value="Instantly find a script within the database. E.g.: &scripts snipecalc",
            inline=False
        )

        embed.add_field(
            name="`/group_scripts`",
            value="Combine scripts into one to improve loading times using the TW Extension.",
            inline=False
        )

        embed.add_field(
            name="`/am`",
            value="Displays a interactive menu to browse through differenct AM templates. Find the one for you and quickly import it ingame.",
            inline=False
        )

        embed.add_field(
            name="`&am <template_name>`",
            value="Instantly find a template within the database. E.g.: &am def",
            inline=False
        )

        embed.add_field(
            name="`/purge`",
            value="Delete messages from the current channel. Be cautious using this! Administrator only. ",
            inline=False
        )
        
        embed.add_field(
            name="`Report to mods`",
            value="Report messages to the server moderators using right-click > apps > report to mods.",
            inline=False
        )

        embed.add_field(
            name="`&setmodchannel <channel_name>",
            value="Set the moderator-only channel to use for reported messages. E.g.: &setmodchannel #moderator-only",
            inline=False
        )
        
        embed.add_field(
            name="`&bothelp`",
            value="Shows the current help menu.",
            inline=False
        )
        
        footer_icon_url = "https://i.imgur.com/N6Z8wxx.png"
        embed.set_footer(text="Use commands with prefixes '&' or '/' as stated\nTribalWars Library - Created by Victorious")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
