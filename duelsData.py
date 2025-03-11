import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import time

from pymongo.errors import DuplicateKeyError

from test_db import player1_id

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))



def create_server_database(server_id):
    db = client[f'duels_{server_id}']
    if 'duels_history' not in db.list_collection_names():
        db.create_collection('duels_history')
    if 'ongoing_duels' not in db.list_collection_names():
        db.create_collection('ongoing_duels')
    if 'players' not in db.list_collection_names():
        db.create_collection('players')
    return db


def register_player(player_id):
    db = client['MONGODB_URI']
    players_table = db['players']
    players_table.create_index("handle", unique=True)
    player_data = {
            # "user_id": str(user_id),
            "handle": player_id,
            # "discord_name": discord_name,
            "rating": 1500,
            "max_rating": 1500,
            "elo" : 10,
            "wins": 0,
            "losses": 0,
            "registration_time": time()
        }

    try:
        players_table.insert_one(player_data)
        return f"Player registered with handle : { player_id }!"
    except DuplicateKeyError:
        return f"Error: Codeforces handle : '{player_id}' is already registered."

      
def create_duel(server_id, player1_id, player1_rating, player2_id, player2_rating, questions):
    db = create_server_database(server_id)
    current_time = datetime.now()
    player1 = db.players.find_one({"user_id": str(player1_id)})
    player2 = db.players.find_one({"user_id": str(player2_id)})

 #register missing players

    if not player1:
        register_player(player1_id)
        player1 = db.players.find_one({"user_id": str(player1_id)})  # Re-fetch after registration

    if not player2:
        register_player(player2_id)
        player2 = db.players.find_one({"user_id": str(player2_id)})  # Re-fetch after registration

    # player1 = db.players.find_one({"user_id": str(player1_id)})
    # player2 = db.players.find_one({"user_id": str(player2_id)})
    #
    # if not player1 or not player2:
    #     missing_players = []
    #     if not player1:
    #         missing_players.append(f"<@{player1_id}>")
    #     if not player2:
    #         missing_players.append(f"<@{player2_id}>")
    #
    #
    #     return f"Error: The following players are not registered: {', '.join(missing_players)}. They need to register before starting a duel."


    duel_data = {
        'server_id': server_id,
        'date': current_time.date().isoformat(),
        'time': current_time.time().isoformat(),
        'player1_id': player1_id,
        'player1_rating': player1_rating,
        'player2_id': player2_id,
        'player2_rating': player2_rating,
        'questions': questions,
        'miscellaneous': None,
        'status': 'pending',
        'winner': None,
        'score': None
    }
    

    duel_id = f"{server_id}_{player1_id}_{player2_id}"# should change this

    duel_data['duel_id'] = duel_id

    db.duels_history.insert_one(duel_data)
    
    return duel_id

def accept_duel(server_id, player1_id, player2_id):
    db = client[f'duels_{server_id}']
    
    duel = db.duels_history.find_one({'status': 'pending', 'player1_id': player1_id, 'player2_id': player2_id})

    if duel:
        current_time = datetime.now()
        
        ongoing_duel_data = {
            'duel_id': duel['duel_id'],
            'server_id': server_id,
            'date': current_time.date().isoformat(),
            'time': current_time.time().isoformat(),
            'player1_id': duel['player1_id'],
            'player1_rating': duel['player1_rating'],
            'player2_id': duel['player2_id'],
            'player2_rating': duel['player2_rating'],
            'questions': duel['questions'],
            'miscellaneous': None,
            'status': 'ongoing'
        }
        
        db.ongoing_duels.insert_one(ongoing_duel_data)
        
        # Update status in history to ongoing as well
        db.duels_history.update_one({'_id': duel['_id']}, {'$set': {'status':'ongoing'}})

def end_duel(server_id, player1_id, player2_id, winner, score):
    db = client[f'duels_{server_id}']
    
    duel_query = {'status':'ongoing', 'player1_id': player1_id, 'player2_id': player2_id}
    
    ongoing_duel = db.ongoing_duels.find_one(duel_query)
    
    if ongoing_duel:
        db.duels_history.update_one(
            {'duel_id': ongoing_duel['duel_id']},
            {'$set':
                {
                    'status':'finished',
                    'winner': winner,
                    'score': score
                }}
        )       
        db.ongoing_duels.delete_one(duel_query)



def get_pending_duel(server_id, player1_id, player2_id):
    db = client[f'duels_{server_id}']
    
    return db.duels_history.find_one({'status':'pending', 'player1_id': player1_id,'player2_id' : player2_id})

def get_duel_history(server_name):
    db = client[f'duels_{server_name}']
    
    return list(db.duels_history.find())


