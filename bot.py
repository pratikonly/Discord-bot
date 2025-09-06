import discord
from discord.ext import commands
import asyncio
import requests
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

API_URL = os.getenv('API_URL')  # e.g., https://your-project.vercel.app/api/upload
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

CATEGORIES = {
    '🎉': 'Entertainment',
    '📚': 'Education',
    '🌐': 'Website',
    '🛠️': 'Hack',
    '❓': 'Others'
}

@bot.event
async def on_ready():
    print(f'Bot is ready: {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await message.delete()

    prompt = await message.channel.send(
        f"Choose a category for your message:\n"
        f"🎉 Entertainment\n"
        f"📚 Education\n"
        f"🌐 Website\n"
        f"🛠️ Hack\n"
        f"❓ Others"
    )

    for emoji in CATEGORIES.keys():
        await prompt.add_reaction(emoji)

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) in CATEGORIES and reaction.message.id == prompt.id

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        tag = CATEGORIES[str(reaction.emoji)]

        tagged_message = f"[{tag}] {message.content}"
        await message.channel.send(tagged_message)

        payload = {'message': message.content, 'tag': tag}
        response = requests.post(API_URL, json=payload)
        if response.status_code != 200:
            print(f"Upload failed: {response.text}")

        await prompt.delete()

    except asyncio.TimeoutError:
        await prompt.delete()

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
