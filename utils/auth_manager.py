import requests
import datetime
from pymongo import MongoClient

class AuthManager:
    def __init__(self, client_id, client_secret, db_name):
        self.client_id = client_id
        self.client_secret = client_secret

        # Connexion à MongoDB
        self.client = MongoClient("mongodb://feliciadossou:Femaliendos8@cluster0.mongodb.net/ProjetM1?retryWrites=true&w=majority")
        self.db = self.client[db_name]
    
    def get_token(self):
        """Récupère un token valide, renouvelé si nécessaire"""
        token_data = self.db['SpotifyTokens'].find_one()

        if token_data is None or self.is_token_expired(token_data):
            token_data = self.request_new_token()
            self.store_token(token_data)
        
        return token_data['access_token']
    
    def is_token_expired(self, token_data):
        """Vérifie si le token a expiré"""
        expires_in = token_data['expires_in']
        timestamp = token_data['timestamp']
        return datetime.datetime.utcnow() > (timestamp + datetime.timedelta(seconds=expires_in))

    def request_new_token(self):
        """Obtient un nouveau token depuis l'API Spotify"""
        url = "https://accounts.spotify.com/api/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            token_info = response.json()
            token_info['timestamp'] = datetime.datetime.utcnow()
            return token_info
        else:
            raise Exception("Impossible de récupérer le token.")

    def store_token(self, token_data):
        """Stocke le nouveau token dans MongoDB"""
        self.db['SpotifyTokens'].update_one({}, {'$set': token_data}, upsert=True)
        print("Token mis à jour dans la base de données.")
