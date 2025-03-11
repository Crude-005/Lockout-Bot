import discord
import os

from leaderboard import send_leaderboard
from userVerification import userRegistration
from dotenv import load_dotenv
from duel import initiate_duel
from duelsData import create_duel, accept_duel, get_pending_duel
from linkDiscord import (
    discord_register_player,
    discord_create_duel,
    discord_accept_duel,
    discord_end_duel,
    discord_show_history,
)

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
        opponent = message.mentions[0]

        if challenger == opponent:
            await message.channel.send("You cannot duel yourself!")
            return

        questions = ["Question 1", "Question 2", "Question 3"]  # Example questions for the duel
        await discord_create_duel(message.guild.id, challenger, opponent, questions, message.channel)
        return

    if message.content.startswith("$acceptduel"):
        if len(message.mentions) != 1:
            await message.channel.send("Usage: `$acceptduel @challenger`")
            return

        challenger = message.mentions[0]
        await discord_accept_duel(message.guild.id, challenger, message.author, message.channel)
        return

    if message.content.startswith("$history"):
        await discord_show_history(message.guild.name, message.channel)
        return

if __name__ == "__main__":
    client.run(os.getenv('BOT_TOKEN'))
