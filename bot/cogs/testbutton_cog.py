class TestButtonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="testbutton")
    async def testbutton(self, ctx):
        embed = discord.Embed(title="Test Button", description="Click the button below.")
        view = TestView()
        await ctx.send(embed=embed, view=view)

class TestView(discord.ui.View):
    @discord.ui.button(label="Test Resolve", style=discord.ButtonStyle.success)
    async def test_resolve(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.disabled = True
        embed = interaction.message.embeds[0]
        embed.title = "Resolved Test"
        embed.add_field(name="Resolved by", value=interaction.user.mention, inline=False)

        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("Test resolved successfully.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TestButtonCog(bot))