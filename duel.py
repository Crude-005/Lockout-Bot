import discord
import asyncio
from pymongo import MongoClient
from datetime import datetime, timedelta
import requests

client = discord.Client(intents=discord.Intents.all())

mongo_client = MongoClient('localhost', 27017)
db = mongo_client['LockoutBot']
users_collection = db['users']
questions_collection = db['questions']

def get_questions(rating, user1, user2):
    difficulties = [rating - 200, rating - 100, rating + 100, rating + 200]

    questions = list(questions_collection.find({
        "rating": {"$in": difficulties},
        "locked": False,
        "solved_by": {"$nin": [user1, user2]}
    }).limit(4))

    if len(questions) == 4:
        questions_collection.update_many(
            {"_id": {"$in": [q["_id"] for q in questions]}}, {"$set": {"locked": True}}
        )

    return questions if len(questions) == 4 else []

async def initiate_duel(challenger, challenged, channel):
    await channel.send(f"Challenger: {challenger.name}, Challenged: {challenged.name}")  # Debug message

    challenger_data = users_collection.find_one({"discord_id": str(challenger.id)})
    challenged_data = users_collection.find_one({"discord_id": str(challenged.id)})

    if not challenger_data or not challenged_data:
        await channel.send("One or both participants are not registered.")  # Debug message
        await channel.send("Both participants need to be registered to start a duel.")

        return

    await channel.send(f"Sending duel challenge message to {challenged.name}")  # Debug message
    await channel.send(
        f"{challenged.mention}, you have been challenged by {challenger.mention}! Type `$accept` to accept or `$decline` to decline. You have 10 minutes.")

    def check_acceptance(m):
        return m.author == challenged and m.content.lower() in ["$accept", "$decline"]

    try:
        response = await client.wait_for("message", timeout=600, check=check_acceptance)

        if response.content.lower() == "$decline":
            await channel.send(f"{challenged.mention} has declined the challenge.")

            return

    except asyncio.TimeoutError:
        await channel.send(f"{challenged.mention} did not respond in time. The challenge is canceled.")

        return

    lower_rating = min(challenger_data['rating'], challenged_data['rating'])
    questions = get_questions(lower_rating, str(challenger.id), str(challenged.id))

    if len(questions) < 4:
        await channel.send("Not enough questions available for the duel. Please try again later.")

        return

    points = [100, 200, 300, 400]

    for question, point in zip(questions, points):
        question["points"] = point

    await channel.send(
        f"The duel between {challenger.mention} and {challenged.mention} has started! You have 1 hour to solve the questions."
    )

    duel_data = {
        "challenger": str(challenger.id),
        "challenged": str(challenged.id),
        "questions": questions,
        "scores": {str(challenger.id): 0, str(challenged.id): 0},
        "start_time": datetime.utcnow(),
        "end_time": datetime.utcnow() + timedelta(hours=1),
    }
    db.duels.insert_one(duel_data)

    await manage_duel(duel_data, channel)


def solved_questions(user_id):
    user_data = users_collection.find_one({"discord_id": user_id})
    if not user_data: return []

    handle = user_data.get("handle")
    if not handle: return []

    url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=10"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get("result", [])

    return []


async def manage_duel(duel_data, channel):
    end_time = duel_data['end_time']
    duel_id = duel_data['_id']

    while datetime.utcnow() < end_time:
        await asyncio.sleep(10)

        duel = db.duels.find_one({"_id": duel_id})
        if not duel:
            break

        submissions = {
            duel['challenger']: solved_questions(duel['challenger']),
            duel['challenged']: solved_questions(duel['challenged'])
        }

        updated = False
        for question in duel['questions']:
            if "solved_by" in question:
                continue

            for user_id, user_submissions in submissions.items():
                for sub in user_submissions:
                    if (sub['problem']['contestId'] == question['contestId'] and
                            sub['problem']['index'] == question['index'] and
                            sub['verdict'] == 'OK'):
                        question['solved_by'] = user_id
                        duel['scores'][user_id] += question['points']
                        updated = True
                        break

        if updated:
            db.duels.update_one({"_id": duel_id}, {"$set": {"questions": duel['questions'], "scores": duel['scores']}})

    await announce_winner(duel_id, channel)


def k_factor(rating, r_min=0, r_max=3000, k_max=24.78, k_min=18.31):
    return k_max - (rating - r_min) * (k_max - k_min) / (r_max - r_min)

def expected_score(r1, r2):
    return 1 / (1 + 10 ** ((r2 - r1) / 400))

def update_elo(winner_id, loser_id):
    winner_data = users_collection.find_one({"discord_id": winner_id})
    loser_data = users_collection.find_one({"discord_id": loser_id})

    if not winner_data or not loser_data:
        return None, None  # Ensure both players exist

    # Ensure Elo rating exists, initialize to 1000 if missing
    r1 = winner_data.get('elo_rating', 1000)
    r2 = loser_data.get('elo_rating', 1000)

    k1 = k_factor(r1)
    k2 = k_factor(r2)

    e1 = expected_score(r1, r2)
    e2 = expected_score(r2, r1)

    s1, s2 = 1, 0  # Winner gets 1, loser gets 0

    new_r1 = round(r1 + k1 * (s1 - e1), 2)
    new_r2 = round(r2 + k2 * (s2 - e2), 2)

    # 🔥 **Optimized MongoDB Update in One Query**
    users_collection.update_many(
        {"discord_id": {"$in": [winner_id, loser_id]}},
        {"$set": {winner_id: new_r1, loser_id: new_r2}}
    )

    return new_r1, new_r2


async def announce_winner(duel_id, channel):
    duel = db.duels.find_one({"_id": duel_id})
    scores = duel['scores']
    challenger_score = scores[duel['challenger']]
    challenged_score = scores[duel['challenged']]

    if challenger_score > challenged_score:
        winner, loser = duel['challenger'], duel['challenged']
    else:
        winner, loser = duel['challenged'], duel['challenger']

    new_winner_elo, new_loser_elo = update_elo(winner, loser)

    msg = f"🏆 **Duel Results** 🏆\n\n"
    msg += f"🥇 **Winner:** <@{winner}> (New Elo: {new_winner_elo})\n"
    msg += f"❌ **Loser:** <@{loser}> (New Elo: {new_loser_elo})\n"

    await channel.send(msg)

    # Unlock questions
    for question in duel['questions']:
        questions_collection.update_one({"_id": question["_id"]}, {"$set": {"locked": False}})

    # Remove duel entry
    db.duels.delete_one({"_id": duel_id})




def check_solved(user_id, question):
    user_data = users_collection.find_one({"discord_id": user_id})
    handle = user_data['handle']

    url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=10"
    response = requests.get(url)

    if response.status_code == 200:
        submissions = response.json()['result']

        for submission in submissions:
            if submission['problem']['contestId'] == question['contestId'] and submission['problem']['index'] == question['index']:
                if submission['verdict'] == 'OK':
                    return True

    return False
