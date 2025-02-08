import discord
import os

from leaderboard import send_leaderboard
from userVerification import userRegistration
from dotenv import load_dotenv
from duel import initiate_duel
load_dotenv()

client = discord.Client(intents=discord.Intents.all())

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

    if message.content.startswith("$duel"):
        if len(message.mentions) != 1:
            await message.channel.send("Please mention exactly one user to challenge them to a duel.")
            return

        challenger = message.author
        challenged = message.mentions[0]

        if challenger == challenged:
            await message.channel.send("You cannot duel yourself!")
            return

        await message.channel.send(f"Initiating duel between {challenger.name} and {challenged.name}")  # Debug message
        await initiate_duel(challenger, challenged, message.channel)

    if message.content.startswith("$leaderboard"):
        await send_leaderboard(message)
        return

if __name__ == "__main__":
    client.run(os.getenv('BOT_TOKEN'))
