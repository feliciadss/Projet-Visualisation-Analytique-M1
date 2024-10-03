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
        self.album_id = track_json.get('album_id')
        # Ajouter les nouvelles caractéristiques musicales
        self.tempo = track_json.get('audio_features', {}).get('tempo')
        self.energy = track_json.get('audio_features', {}).get('energy')
        self.danceability = track_json.get('audio_features', {}).get('danceability')
        self.acousticness = track_json.get('audio_features', {}).get('acousticness')
        self.valence = track_json.get('audio_features', {}).get('valence')
        self.duration_ms = track_json.get('audio_features', {}).get('duration_ms')

# Classe pour représenter un Artiste
class Artist:
    def __init__(self, artist_json):
        self.id = artist_json.get('id')
        self.name = artist_json.get('name')
        self.popularity = artist_json.get('popularity')  # Popularité de l'artiste
        self.followers = artist_json.get('followers', {}).get('total')  # Nombre d'abonnés
        self.genre = artist_json.get('genre')
        self.market = artist_json.get('market')  # Pays d'origine de l'artiste

class DataManager:
    def __init__(self):
        self.tracks_collection = get_collection_from_db('tracks')
        self.artists_collection = get_collection_from_db('artists')

    # Fonction pour créer un DataFrame de popularité des genres par pays
    def create_genre_popularity_dataframe(self, genre_filter=None):
        # Filtrer les artistes par genre si nécessaire
        artists_cursor = self.artists_collection.find({"genre": genre_filter}) if genre_filter else self.artists_collection.find()
        artists_list = list(artists_cursor)

        # Préparer une liste des données pour construire le DataFrame
        data = []
        for artist_json in artists_list:
            artist = Artist(artist_json)

            # Ajouter l'artiste à la liste de données
            if artist.market and artist.popularity:
                data.append({
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'artist_genre': artist.genre,
                    'artist_market': artist.market,
                    'artist_popularity': artist.popularity
                })

        # Construire le DataFrame
        df = pd.DataFrame(data)

        # Si le DataFrame n'est pas vide, calculer la popularité moyenne par pays
        if not df.empty:
            df_popularity = df.groupby('artist_market')['artist_popularity'].mean().reset_index()
            df_popularity.columns = ['artist_market', 'average_popularity']  # Renommer les colonnes
            return df_popularity
        else:
            return pd.DataFrame()  # Retourner un DataFrame vide si aucun artiste n'a été trouvé
