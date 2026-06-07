import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# List of bad words to filter
BAD_WORDS = ['nigger', 'nga', 'nigga', 'abuses', 'abuse']  # Add more words as needed

# Track warnings
user_warnings = {}

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')

@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Ignore other bots
    if message.author.bot:
        return
    
    # Check if message has bad words
    message_lower = message.content.lower()
    has_bad_word = False
    
    for word in BAD_WORDS:
        if word in message_lower:
            has_bad_word = True
            break
    
    if has_bad_word:
        # Get user ID
        user_id = message.author.id
        
        # Add a warning
        if user_id not in user_warnings:
            user_warnings[user_id] = 0
        user_warnings[user_id] += 1
        
        warning_count = user_warnings[user_id]
        
        # Delete the message
        await message.delete()
        
        # Send warning message
        if warning_count < 3:
            embed = discord.Embed(
                title="⚠️ Warning!",
                description=f"{message.author.mention} used abusive language\n**Warnings: {warning_count}/3**",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed, delete_after=5)
        else:
            # Ban after 3 warnings
            embed = discord.Embed(
                title="🚫 Banned!",
                description=f"{message.author.mention} has been banned (3 warnings for abusive language)",
                color=discord.Color.dark_red()
            )
            await message.channel.send(embed=embed)
            await message.guild.ban(message.author, reason="3 warnings for abusive language")
            del user_warnings[user_id]
    
    # Process commands
    await bot.process_commands(message)

# Run the bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERROR: DISCORD_TOKEN not found in .env file")
