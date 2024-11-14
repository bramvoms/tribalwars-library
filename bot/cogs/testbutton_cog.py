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

class TestView(discord.ui.View):
    @discord.ui.button(label="Click Me", style=discord.ButtonStyle.primary)
    async def test_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.info("Button clicked by user: %s", interaction.user)  # Log who clicked the button
        
        # Disable the button to prevent further clicks
        button.disabled = True
        logger.info("Button disabled.")

        # Check for an embed in the original message
        if interaction.message.embeds:
            embed = interaction.message.embeds[0]
            logger.info("Embed found: %s", embed.to_dict())  # Log the current embed state

            # Update the embed's description
            embed.description = "Button clicked!"
            logger.info("Embed description updated.")

            try:
                # Attempt to edit the message with the updated embed and disabled button
                await interaction.message.edit(embed=embed, view=self)
                logger.info("Message edited successfully.")
            except Exception as e:
                logger.error("Failed to edit the message: %s", e)
                await interaction.response.send_message("An error occurred while updating the message.", ephemeral=True)
        else:
            # Log if no embed is found
            logger.warning("No embed found to edit in the message.")
            await interaction.response.send_message("No embed found to edit.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TestButtonCog(bot))
