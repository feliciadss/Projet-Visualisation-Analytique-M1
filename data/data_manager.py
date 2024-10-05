import pandas as pd
from pymongo import MongoClient
import configparser

config = configparser.ConfigParser()
config.read("./data/config.ini")

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

    def create_radar_dataframe(self, selected_genres):
        all_track_data = []
        
        for genre_selectionné in selected_genres:

            # Étape 1 : Récupérer tous les artistes avec le genre sélectionné
            artists = self.artists_collection.find({'genre': genre_selectionné})
            artist_ids = [artist['id'] for artist in artists]

            if not artist_ids:
                print(f"Aucun artiste trouvé pour le genre {genre_selectionné}")
                continue

            # Étape 2 : Récupérer tous les tracks associés à ces artistes
            tracks = list(self.tracks_collection.find({'artists.id': {'$in': artist_ids}}))  # Convertir en liste

            if not tracks:
                print(f"Aucun track trouvé pour les artistes de {genre_selectionné}")
                continue

            # Étape 3 : Extraire les audio features de ces tracks et les stocker dans une liste
            for track in tracks:
                audio_features = track.get('audio_features', {})
                # Ajouter les artistes du track (géré comme un array d'objets)
                track_artists = track.get('artists', [])
                for artist in track_artists:
                    artist_id = artist.get('id')
                    if artist_id in artist_ids:  # Si l'artiste est dans la liste des artistes trouvés
                        track_info = {
                            'track_id': track.get('id'),
                            'name': track.get('name'),
                            'genre': genre_selectionné,
                            'tempo': audio_features.get('tempo'),
                            'energy': audio_features.get('energy'),
                            'danceability': audio_features.get('danceability'),
                            'acousticness': audio_features.get('acousticness'),
                            'valence': audio_features.get('valence'),
                            'duration_ms': audio_features.get('duration_ms')
                        }
                        print(f"Ajout du track : {track_info}")
                        all_track_data.append(track_info)
                        break 
        df = pd.DataFrame(all_track_data)
        return df