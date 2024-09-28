import pandas as pd
from pymongo import MongoClient
import configparser

# Charger la configuration pour MongoDB
config = configparser.ConfigParser()
config.read("./data/config.ini")

# Fonction pour récupérer une collection depuis MongoDB
def get_collection_from_db(collection_name):
    client = MongoClient(config['MONGO_DB']['MONGO_URI'])
    db = client[config['MONGO_DB']['DB_NAME']]
    collection = db[collection_name]
    return collection

# Classe pour représenter un Track
class Track:
    def __init__(self, track_json):
        self.id = track_json.get('id')
        self.name = track_json.get('name')
        self.artists = [artist['id'] for artist in track_json.get('artists', [])]  # Liste des IDs des artistes
        self.market = track_json.get('market')
        self.album_id = track_json.get('album_id')

# Classe pour représenter un Artiste
class Artist:
    def __init__(self, artist_json):
        self.id = artist_json.get('id', 'Unknown ID')
        self.genre = artist_json.get('genre', 'Unknown Genre')
        self.market = artist_json.get('market', 'Unknown Market')  # Assure un marché par défaut

class DataManager:
    def __init__(self):
        self.tracks_collection = get_collection_from_db('tracks')
        self.artists_collection = get_collection_from_db('artists')

    def create_tracks_artists_dataframe(self, genre_filter=None):
        tracks_cursor = self.tracks_collection.find()
        tracks_list = list(tracks_cursor)

        data = []
        
        # Parcourir chaque track pour extraire les artistes et leur marché
        for track_json in tracks_list:
            track_id = track_json.get('id')
            track_artists = track_json.get('artists', [])  # Liste des artistes associés à ce track
            
            # Parcourir les artistes associés à chaque track
            for artist_info in track_artists:
                artist_id = artist_info.get('id')
                artist_json = self.artists_collection.find_one({"id": artist_id})
                
                if artist_json:
                    artist = Artist(artist_json)
                    # Filtrer par genre si un genre est spécifié
                    if genre_filter is None or artist.genre == genre_filter:
                        # Vérification que l'artiste a un marché et un genre
                        if artist.market and artist.market != 'Unknown Market':
                            # Ajout de l'artiste au DataFrame
                            data.append({
                                'track_id': track_id,
                                'artist_id': artist.id,
                                'artist_genre': artist.genre,
                                'artist_market': artist.market
                            })
                # Pas besoin de else, car on n'ajoute rien si l'artiste n'existe pas ou ne correspond pas

        # Créer un DataFrame avec les informations extraites
        df = pd.DataFrame(data)

        if not df.empty:
            # Compter la fréquence des marchés (pays) pour chaque artiste
            market_counts = df['artist_market'].value_counts()
            print("Répartition par marché :", market_counts)

        return df
