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
BAD_WORDS = ['nigger', 'nga', 'nigga', 'abuses', 'abuse']

# Track warnings
user_warnings = {}

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    print('Bot is ready to monitor messages!')

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
        if word.lower() in message_lower:
            has_bad_word = True
            print(f"Bad word detected: {word} in message: {message.content}")
            break
    
    if has_bad_word:
        try:
            # Get user ID
            user_id = message.author.id
            
            # Add a warning
            if user_id not in user_warnings:
                user_warnings[user_id] = 0
            user_warnings[user_id] += 1
            
            warning_count = user_warnings[user_id]
            
            print(f"Warning {warning_count} for {message.author}: {message.content}")
            
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
                # Send report to admin (you) instead of banning
                embed = discord.Embed(
                    title="📋 Report - User Reached 3 Warnings",
                    description=f"**User:** {message.author.mention}\n**Username:** {message.author.name}\n**User ID:** {user_id}\n**Reason:** 3 warnings for abusive language",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Action Required", value="Please review and decide on action (ban, kick, etc.)", inline=False)
                
                # Post in channel
                await message.channel.send(f"⚠️ {message.author.mention} has received 3 warnings. Report sent to moderators.")
                del user_warnings[user_id]
        except Exception as e:
            print(f"Error: {e}")
    
    # Process commands
    await bot.process_commands(message)

# Run the bot
if TOKEN:
    print("Starting bot...")
    bot.run(TOKEN)
else:
    print("ERROR: DISCORD_TOKEN not found in .env file")
