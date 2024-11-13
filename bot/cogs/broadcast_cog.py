import discord
from discord.ext import commands
from main import create_embed  # Ensure create_embed is correctly accessible from main.py

class BroadcastCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update")
    @commands.is_owner()  # Ensures only the bot owner can run this command
    async def update(self, ctx, *, message: str):
        # Create the embed using the pre-configured format
        embed = create_embed(title="Update Notification", description=message)

        # List of target channel names to look for
        target_channels = ["algemeen", "general", "scripts"]

        for guild in self.bot.guilds:
            # Step 1: Look for exact matches
            channel = None
            for target_name in target_channels:
                channel = discord.utils.get(guild.text_channels, name=target_name)
                if channel:
                    break  # Stop if an exact match is found

            # Step 2: If no exact match, search for partial matches
            if not channel:
                for target_name in target_channels:
                    channel = next((ch for ch in guild.text_channels if target_name in ch.name.lower() and ch.permissions_for(guild.me).send_messages), None)
                    if channel:
                        break  # Stop if a partial match is found

            # Step 3: If no partial match, use the default system channel
            if not channel:
                channel = guild.system_channel  # Often the welcome channel

            # Step 4: Send the embed if a channel is found
            if channel:
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    print(f"Could not send message to {guild.name} (permission issue)")
            else:
                print(f"No suitable channel found in {guild.name}")

        await ctx.send("Broadcast completed.")

# Setup function to add the cog
def setup(bot):
    bot.add_cog(BroadcastCog(bot))
