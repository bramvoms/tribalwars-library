import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button
from main import create_embed

class AMCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="am", description="Displays rush and template options for AM")
    async def am(self, interaction: Interaction):
        embed = create_embed("Choose an action:", "Select one of the options below for more information.")
        await interaction.response.send_message(embed=embed, view=AMView(), ephemeral=True)

class AMView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_button("Opslag rush", self.opslag_rush_callback)
        self.add_button("ZC rush", self.zc_rush_callback)
        self.add_button("AH rush", self.ah_rush_callback)
        self.add_button("Muur rush", self.muur_rush_callback)
        self.add_button("Toren rush", self.toren_rush_callback)
        self.add_button("Kerk rush", self.kerk_rush_callback)
        self.add_button("Muur spoed", self.muur_spoed_callback)
        self.add_button("OFF sjabloon", self.off_sjabloon_callback)
        self.add_button("DEF sjabloon", self.def_sjabloon_callback)

    def add_button(self, label, callback):
        button = Button(label=label, style=discord.ButtonStyle.primary)
        button.callback = callback
        self.add_item(button)

    async def opslag_rush_callback(self, interaction: Interaction):
        embed = create_embed("Opslag rush", "Placeholder text for Opslag rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def zc_rush_callback(self, interaction: Interaction):
        embed = create_embed("ZC rush", "Placeholder text for ZC rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def ah_rush_callback(self, interaction: Interaction):
        embed = create_embed("AH rush", "Placeholder text for AH rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def muur_rush_callback(self, interaction: Interaction):
        embed = create_embed("Muur rush", "Placeholder text for Muur rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def toren_rush_callback(self, interaction: Interaction):
        embed = create_embed("Toren rush", "Placeholder text for Toren rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def kerk_rush_callback(self, interaction: Interaction):
        embed = create_embed("Kerk rush", "Placeholder text for Kerk rush.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def muur_spoed_callback(self, interaction: Interaction):
        embed = create_embed("Muur spoed", "Placeholder text for Muur spoed.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def off_sjabloon_callback(self, interaction: Interaction):
        embed = create_embed("OFF sjabloon", "Placeholder text for OFF sjabloon.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def def_sjabloon_callback(self, interaction: Interaction):
        embed = create_embed("DEF sjabloon", "Placeholder text for DEF sjabloon.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AMCog(bot))

