import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from instagram_scraper import InstagramScraper

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# BOT setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Create an instance of InstagramScraper
instagram_scraper = InstagramScraper()

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")
    check_instagram.start()
    print("Started checking for new posts...")

@tasks.loop(minutes=15)
async def check_instagram():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel with ID {CHANNEL_ID} not found.")
        return

    try:
        new_post = instagram_scraper.check_for_update()
        if new_post:
            await channel.send(f"New post detected! Check it out: {new_post}")
        else:
            print("No new post detected.")
    except Exception as e:
        print(f"Error checking Instagram: {e}")

# Run the bot
bot.run(TOKEN)