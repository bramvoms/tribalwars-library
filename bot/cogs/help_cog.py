import discord
from discord.ext import commands
from main import create_embed

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bothelp", help="Overzicht van alle commands van de TribalWars Library bot.")
    async def help_command(self, ctx):
        # Create an embed for the help menu
        embed = create_embed(
            title=f"━ TribalWars Library ━",
            description="Hieronder een lijst met alle mogelijkheden in de TribalWars Library bot."
        )

        # Add a short description for each command
        embed.add_field(
            name="`/scripts`",
            value="Toont een interactief menu om scripts te zoeken. Blader door categorieën of gebruik de zoekfunctie.",
            inline=False
        )

        embed.add_field(
            name="`&scripts <script_name>`",
            value="Zoek direct een script in de database. Houdt rekening met typfouten. Bijvoorbeeld: &scripts snipecalc",
            inline=False
        )

        embed.add_field(
            name="`/group_scripts`",
            value="Groepeer scripts tot één script om laadtijden met de TW Extensie te versnellen.",
            inline=False
        )

        embed.add_field(
            name="`/am`",
            value="Toont een interactief menu om AM sjablonen te zoeken.",
            inline=False
        )

        embed.add_field(
            name="`&am <template_name>`",
            value="Zoek direct een AM sjabloon in de database. Houdt rekening met typfouten. Bijvoorbeeld: &am def",
            inline=False
        )

        embed.add_field(
            name="`/purge`",
            value="Verwijder berichten uit het huidige kanaal. Administrator rechten benodigd.",
            inline=False
        )

        embed.add_field(
            name="`&bothelp`",
            value="Toont dit menu.",
            inline=False
        )
        
        footer_icon_url = "https://i.imgur.com/N6Z8wxx.png"
        embed.set_footer(text="Gebruik commands met '&' of '/' zoals hierboven benoemd\nTribalWars Library - Created by Victorious")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
