import json

def load_leaderboard_data():
    with open("mock_data.json", "r") as file:
        data = json.load(file)
    return data

def format_leaderboard(data):
    leaderboard = "Leaderboard:\n"
    sorted_data = sorted(data, key=lambda x: x["score"])
    for idx, user in enumerate(sorted_data, start=1):
        leaderboard += f"{idx}. {user['name']} - {user['rating']} \n"
    return leaderboard

async def send_leaderboard(message):
    data = load_leaderboard_data()
    leaderboard = format_leaderboard(data)
    await message.channel.send(leaderboard)
