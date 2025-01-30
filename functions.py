import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class DuelsDatabase:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
    
    def create_server_database(self, server_id):
        db = self.client[f'duels_{server_id}']
        # Create collections if they don't exist
        if 'ongoing_duels' not in db.list_collection_names():
            db.create_collection('ongoing_duels')
        if 'duels_history' not in db.list_collection_names():
            db.create_collection('duels_history')
        return db
    
    def create_duel(self, server_id, player1_id, player1_rating, player2_id, player2_rating, questions):
        db = self.create_server_database(server_id)
        current_time = datetime.now()
        duel_id = f"{server_id}_{player1_id}_{player2_id}"
        
        duel_data = {
            'server_id': server_id,
            'date': current_time.date().isoformat(),
            'time': current_time.time().isoformat(),
            'player1_id': player1_id,
            'player1_rating': player1_rating,
            'player2_id': player2_id,
            'player2_rating': player2_rating,
            'questions': questions,
            'misc': {}
        }
        
        history_data = {
            'duel_id': duel_id,
            'player1_id': player1_id,
            'player2_id': player2_id,
            'status': 'ongoing',
            'date': current_time.date().isoformat(),
            'time': current_time.time().isoformat(),
            'winner': None,
            'score': None
        }
        
        db.ongoing_duels.insert_one(duel_data)
        db.duels_history.insert_one(history_data)
        return duel_id
    
    def end_duel(self, server_id, duel_id, winner, score):
        db = self.client[f'duels_{server_id}']
        
        # Update history
        db.duels_history.update_one(
            {'duel_id': duel_id},
            {
                '$set': {
                    'status': 'finished',
                    'winner': winner,
                    'score': score
                }
            }
        )
        
        # Remove from ongoing duels
        db.ongoing_duels.delete_one({'server_id': server_id})
    
    def get_ongoing_duel(self, server_id):
        db = self.client[f'duels_{server_id}']
        return db.ongoing_duels.find_one({'server_id': server_id})
    
    def get_duel_history(self, server_id):
        db = self.client[f'duels_{server_id}']
        return list(db.duels_history.find())
