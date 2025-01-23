import discord
import os

from verifyUser import userRegistration
from dotenv import load_dotenv 
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
    elif message.content.startswith("$duel"):
        return
        


if __name__ == "__main__":
    client.run(os.getenv('BOT_TOKEN'))
