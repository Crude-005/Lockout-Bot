import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))

def create_server_database(server_id):
    db = client[f'duels_{server_id}']
    if 'duels_history' not in db.list_collection_names():
        db.create_collection('duels_history')
    if 'ongoing_duels' not in db.list_collection_names():
        db.create_collection('ongoing_duels')
    return db

def create_duel(server_id, player1_id, player1_rating, player2_id, player2_rating, questions):
    db = create_server_database(server_id)
    current_time = datetime.now()
    
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
    
    duel_id = f"{server_id}_{player1_id}_{player2_id}"
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
