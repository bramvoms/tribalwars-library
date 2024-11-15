import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from typing import List, Optional, Literal
from urllib.parse import quote

class MapCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.worlds = []

    async def fetch_worlds(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://dkspeed.jrsoft.tech/api/worlds') as response:
                    if response.status == 200:
                        self.bot.worlds = await response.json()
                        print(f"Updated worlds: {self.bot.worlds}")
        except Exception as e:
            print(f"Failed to fetch worlds: {e}")

    async def cog_load(self):
        """Run tasks when the cog is loaded."""
        await self.fetch_worlds()

    def build_array_params(self, items: str, param_name: str) -> str:
        items_list = [item.strip() for item in items.split(',')]
        return '&'.join([f"{param_name}[]={quote(item)}" for item in items_list])

    @app_commands.command(name="map", description="Get a map link for specified world and type")
    @app_commands.describe(
        world="The world name to get map for",
        type="Type of the map view"
    )
    async def map_command(
        self,
        interaction: discord.Interaction,
        world: str,
        type: Literal["top-ally", "top-players", "villages-all", "villages-tribe-by", "villages-player-by"],
        tribes: Optional[str] = None,
        players: Optional[str] = None
    ):
        await interaction.response.defer()

        if world not in self.bot.worlds:
            await interaction.followup.send(f"Invalid world. Available worlds: {', '.join(self.bot.worlds)}", ephemeral=True)
            return

        if type == "villages-tribe-by" and not tribes:
            await interaction.followup.send("Tribes parameter is required for villages-tribe-by type", ephemeral=True)
            return

        if type == "villages-player-by" and not players:
            await interaction.followup.send("Players parameter is required for villages-player-by type", ephemeral=True)
            return

        base_url = f"https://dkspeed.jrsoft.tech/map/{world}/{type}"
        if type == "villages-tribe-by" and tribes:
            params = self.build_array_params(tribes, "tribes")
            api_url = f"{base_url}?{params}&onlyLink=true"
        elif type == "villages-player-by" and players:
            params = self.build_array_params(players, "players")
            api_url = f"{base_url}?{params}&onlyLink=true"
        else:
            api_url = f"{base_url}?onlyLink=true"

        print(f"Calling API URL: {api_url}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        map_url = data.get("url")

                        embed = discord.Embed(title=f"Map for {world}", color=discord.Color.blue())
                        if type == "villages-tribe-by":
                            embed.description = f"Tribes: {tribes}"
                        elif type == "villages-player-by":
                            embed.description = f"Players: {players}"
                        embed.set_image(url=map_url)
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send(
                            f"Failed to get map. Status: {response.status}",
                            ephemeral=True
                        )
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

    @map_command.autocomplete('world')
    async def world_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=world, value=world)
            for world in self.bot.worlds if current.lower() in world.lower()
        ][:25]

    @map_command.autocomplete('tribes')
    async def tribes_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        if interaction.namespace.type != "villages-tribe-by":
            return []  # Return no options for other types
        return [
            app_commands.Choice(name=f"Tribe {i+1}", value=f"Tribe{i+1}")
            for i in range(10)  # Example tribes
        ]

    @map_command.autocomplete('players')
    async def players_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        if interaction.namespace.type != "villages-player-by":
            return []  # Return no options for other types
        return [
            app_commands.Choice(name=f"Player {i+1}", value=f"Player{i+1}")
            for i in range(10)  # Example players
        ]

async def setup(bot):
    await bot.add_cog(MapCog(bot))
