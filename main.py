import discord
import os

from leaderboard import send_leaderboard
from userVerification import userRegistration
from dotenv import load_dotenv 
from duelsData import create_duel, accept_duel, get_pending_duel
load_dotenv() 



client  = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print("we have logged in as ",client.user)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$verify"):
        await userRegistration(message)
        return

    if message.content.startswith("$leaderboard"):
        await send_leaderboard(message)
        return

    elif message.content.startswith("$duel"):
        parts = message.content.split()
        if len(parts) != 2 or not message.mentions:
            await message.channel.send("Usage: `$duel @opponent`")
            return
        
        opponent = message.mentions[0]
        duel_id = create_duel(message.guild.id, message.author.id, opponent.id)
        
        await message.channel.send(
            f"{opponent.mention}, you have been challenged by {message.author.mention}! "
            f"Type `$acceptduel @{message.author}` to accept."
        )
        return
    
    elif message.content.startswith("$acceptduel"):
        parts = message.content.split()
        if len(parts) != 2 or not message.mentions:
            await message.channel.send("Usage: `$acceptduel @challenger`")
            return
        
        challenger = message.mentions[0]
        duel = get_pending_duel(message.guild.id, challenger.id, message.author.id)

        if not duel:
            await message.channel.send("No pending duel found!")
            return
        
        accept_duel(message.guild.id, challenger.id, message.author.id)
        
        await message.channel.send(
            f"Duel accepted between {challenger.mention} and {message.author.mention}! Good luck!"
        )
        return
        


if __name__ == "__main__":
    client.run(os.getenv('BOT_TOKEN'))
