import discord
from discord.ext import commands

class TestButtonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="testbutton")
    async def testbutton(self, ctx):
        """Command to send a test message with a button."""
        embed = discord.Embed(title="Test Button", description="Click the button below.")
        view = TestView()
        await ctx.send(embed=embed, view=view)

class TestView(discord.ui.View):
    @discord.ui.button(label="Click Me", style=discord.ButtonStyle.primary)
    async def test_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Disable the button to prevent further clicks
        button.disabled = True

        # Edit the original message to display "Button clicked!" and disable the button
        await interaction.message.edit(content="Button clicked!", view=self)

async def setup(bot):
    await bot.add_cog(TestButtonCog(bot))
