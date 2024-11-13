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
        title = f"━ UPDATE ━"
        embed = create_embed(title=title, description=message)

        # List of prioritized channel name patterns
        priority_channels = [
            ["bot messages", "bot berichten"],  # Highest priority: channels for bot messages
            ["scripts"],  # Second priority: "scripts" or similar
            ["algemeen", "general"],  # Third priority: "algemeen" or "general"
        ]

        successful_sends = 0  # Counter for successful sends

        for guild in self.bot.guilds:
            channel = None

            # Step 1: Check each priority level for matches
            for channel_keywords in priority_channels:
                for keyword in channel_keywords:
                    channel = next((ch for ch in guild.text_channels if keyword in ch.name.lower() and ch.permissions_for(guild.me).send_messages), None)
                    if channel:
                        break  # Stop searching if a match is found
                if channel:
                    break  # Move to the next guild if a channel is found

            # Step 2: Use the system channel as a fallback if no matches found
            if not channel:
                channel = guild.system_channel  # Often the welcome channel

            # Step 3: Send the embed if a channel is found
            if channel:
                try:
                    await channel.send(embed=embed)
                    successful_sends += 1  # Increment successful send count
                except discord.Forbidden:
                    print(f"Could not send message to {guild.name} (permission issue)")
            else:
                print(f"No suitable channel found in {guild.name}")

        # Step 4: Send a confirmation message with the number of servers updated
        await ctx.send(f"Update verzonden naar {successful_sends} servers.")

# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(BroadcastCog(bot))
