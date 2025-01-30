import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from functions import DuelsDatabase

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
db = DuelsDatabase()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='startduel')
async def start_duel(ctx, player2: discord.Member, p1_rating: int, p2_rating: int, *questions):
    duel_id = db.create_duel(
        ctx.guild.id,
        ctx.author.id,
        p1_rating,
        player2.id,
        p2_rating,
        list(questions)
    )
    await ctx.send(f'Duel started! ID: {duel_id}')

@bot.command(name='endduel')
async def end_duel(ctx, winner: discord.Member, score: str):
    duel = db.get_ongoing_duel(ctx.guild.id)
    if not duel:
        await ctx.send('No ongoing duel found!')
        return
    
    duel_id = f"{ctx.guild.id}_{duel['player1_id']}_{duel['player2_id']}"
    db.end_duel(ctx.guild.id, duel_id, winner.id, score)
    await ctx.send(f'Duel ended! Winner: {winner.mention}')

@bot.command(name='duelhistory')
async def duel_history(ctx):
    history = db.get_duel_history(ctx.guild.id)
    if not history:
        await ctx.send('No duel history found!')
        return
    
    history_text = '\n'.join([
        f"Duel {h['duel_id']}: {h['status']}, Winner: {h['winner']}, Score: {h['score']}"
        for h in history
    ])
    await ctx.send(f'Duel History:\n{history_text}')

bot.run(os.getenv('DISCORD_TOKEN'))
