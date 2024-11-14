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
    async def test_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            # Directly respond to the interaction with a simple message
            await interaction.response.send_message("Button clicked!", ephemeral=True)
            print("Interaction response sent successfully.")  # For debugging
        except Exception as e:
            # Log any errors to understand where the issue may lie
            print(f"Error in interaction: {e}")

async def setup(bot):
    await bot.add_cog(TestButtonCog(bot))
