from duelsData import register_player, create_duel, accept_duel, end_duel, get_pending_duel, get_duel_history
import discord

async def discord_register_player(player_id, channel):
    response = register_player(player_id)
    await channel.send(response)

async def discord_create_duel(server_id, challenger, opponent, questions, channel):
    duel_id = create_duel(server_id, challenger.id, 1500, opponent.id, 1500, questions)
    if duel_id:
        await channel.send(
            f"{opponent.mention}, you have been challenged by {challenger.mention}! "
            f"Type `$acceptduel @{challenger.name}` to accept."
        )
    else:
        await channel.send("Error creating duel.")

async def discord_accept_duel(server_id, challenger, opponent, channel):
    pending_duel = get_pending_duel(server_id, challenger.id, opponent.id)
    if pending_duel:
        accept_duel(server_id, challenger.id, opponent.id)
        await channel.send(
            f"Duel accepted between {challenger.mention} and {opponent.mention}! Good luck!"
        )
    else:
        await channel.send("No pending duel found!")

async def discord_end_duel(server_id, player1_id, player2_id, winner_id, score, channel):
    end_duel(server_id, player1_id, player2_id, winner_id, score)
    winner_mention = f"<@{winner_id}>"
    await channel.send(f"Duel ended! Congratulations {winner_mention}, final score: {score}")

async def discord_show_history(server_name, channel):
    history = get_duel_history(server_name)
    if not history:
        await channel.send("No duel history available.")
        return
    
    history_message = "**Duel History:**\n"
    for duel in history[-10:]:  # Show last 10 duels
        history_message += (
            f"{duel['date']} - <@{duel['player1_id']}> vs <@{duel['player2_id']}> - "
            f"Winner: {('<@'+str(duel['winner'])+'>') if duel['winner'] else 'Pending'}\n"
        )
    
    await channel.send(history_message)
