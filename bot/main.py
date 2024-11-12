import discord
from discord import app_commands

# Set up intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Initialize the bot client
class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user}!')
        await self.tree.sync()  # Syncs commands with Discord

client = MyClient(intents=intents)

# Define the FAQs as a dictionary
faqs = {
    "help": "I can help answer frequently asked questions! Try using `/faq <topic>`.",
    "rules": "Please follow the server rules to ensure a friendly environment.",
    "commands": "Available commands are `/faq <topic>`, etc."
}

# Define a slash command for FAQ
@client.tree.command(name="faq", description="Get answers to frequently asked questions")
@app_commands.describe(topic="The FAQ topic you'd like information about")
async def faq(interaction: discord.Interaction, topic: str):
    if topic in faqs:
        await interaction.response.send_message(faqs[topic])
    else:
        await interaction.response.send_message("Sorry, I don’t have information on that topic. Try `/faq help` for more info.")

# Run the bot
client.run(BOT_TOKEN)
