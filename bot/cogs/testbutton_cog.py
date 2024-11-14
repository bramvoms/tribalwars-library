import discord
from discord.ext import commands
import logging

class TestButtonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="testbutton")
    async def testbutton(self, ctx):
        """Command to send a test message with a button."""
        embed = discord.Embed(title="Test Button", description="Click the button below.")
        view = TestView()
        await ctx.send(embed=embed, view=view)

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestView(discord.ui.View):
    @discord.ui.button(label="Click Me", style=discord.ButtonStyle.primary)
    async def test_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Disable the button to prevent further clicks
        button.disabled = True

        # Check for an embed in the original message
        if interaction.message.embeds:
            embed = interaction.message.embeds[0]
            # Update the embed's description
            embed.description = "Button clicked!"

            # Edit the message with the updated embed and disabled button
            await interaction.message.edit(embed=embed, view=self)

            # Send an ephemeral response to confirm the interaction
            await interaction.response.send_message("Interaction processed successfully.", ephemeral=True)
        else:
            # Send a message if no embed is found
            await interaction.response.send_message("No embed found to edit.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TestButtonCog(bot))
