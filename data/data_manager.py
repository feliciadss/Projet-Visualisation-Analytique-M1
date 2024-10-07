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
        self.popularity = artist_json.get('popularity') 
        self.followers = artist_json.get('followers', {}).get('total') 
        self.genre = artist_json.get('genre')
        self.market = artist_json.get('market')
        
class Album:
    def __init__(self, album_json):
        self.id = album_json.get('id')
        self.name = album_json.get('name')
        self.album_type = album_json.get('album_type')
        self.artists = [artist['id'] for artist in album_json.get('artists', [])]
        self.available_markets = album_json.get('available_markets', [])
        self.release_date = album_json.get('release_date')
        self.total_tracks = album_json.get('total_tracks')
        self.uri = album_json.get('uri')
        self.top_market = album_json.get('top_market', [])

class DataManager:
    def __init__(self):
        self.tracks_collection = get_collection_from_db('tracks')
        self.artists_collection = get_collection_from_db('artists')
        self.albums_collection = get_collection_from_db('albums')

    # Fonction pour créer un DataFrame sur les features audios des tracks
    def create_audiofeatures_dataframe(self, selected_genres):
        all_track_data = []
        
        for genre_selectionné in selected_genres:

            artists = self.artists_collection.find({'genres': {'$regex': genre_selectionné, '$options': 'i'}})
            artist_ids = [artist['id'] for artist in artists]

            if not artist_ids:
                print(f"Aucun artiste trouvé pour le genre {genre_selectionné}")
                continue
            
            tracks = list(self.tracks_collection.find({'artists.id': {'$in': artist_ids}}))  # Convertir en liste

            if not tracks:
                print(f"Aucun track trouvé pour les artistes de {genre_selectionné}")
                continue

            for track in tracks:
                audio_features = track.get('audio_features', {})
                track_artists = track.get('artists', [])
                for artist in track_artists:
                    artist_id = artist.get('id')
                    if artist_id in artist_ids: 
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
                        all_track_data.append(track_info)
                        break 
        df = pd.DataFrame(all_track_data)
        return df
    
    # Fonction pour créer un DataFrame avec la popularité des genres par pays
    def create_album_genre_popularity_dataframe(self, selected_genre):  # un seul genre est sélectionné ici
        all_album_data = []
        
        albums = self.albums_collection.find()

        for album in albums:
            album_artists = album.get('artists', [])  
            top_markets = album.get('top_market', [])  
            
            for artist in album_artists:
                artist_data = self.artists_collection.find_one({'id': artist['id'], 'genres': {'$regex': selected_genre, '$options': 'i'}})
                
                if artist_data and top_markets:
                    for market in top_markets:
                        album_info = {
                            'album_id': album.get('id'),
                            'album_name': album.get('name'),
                            'market': market,  
                            'genre': selected_genre  
                        }
                        all_album_data.append(album_info)

        df = pd.DataFrame(all_album_data)
        
        if df.empty:
            return pd.DataFrame()

        df_popularity = df.groupby(['market', 'genre']).size().reset_index(name='popularity')

        return 
    
# Fonction pour créer la matrice des collaborations entre genres
    def create_genre_collaboration_matrix(tracks_collection, artists_collection):
        collaborations = []
        genre_pairs = []

        # Parcourir chaque piste pour récupérer les collaborations entre artistes
        tracks = tracks_collection.find({"$where": "this.artists.length > 1"})
        
        for track in tracks:
            track_artists = track.get('artists', [])
            artist_genres = []

        # Récupérer les genres pour chaque artiste sur la piste
            for artist in track_artists:
                artist_data = artists_collection.find_one({'id': artist['id']})
                if artist_data and artist_data.get('genre'):
                    artist_genres.append(artist_data['genre'])
        
        # Créer des paires de genres à partir des genres récupérés
            for i in range(len(artist_genres)):
                for j in range(i + 1, len(artist_genres)):
                    genre1 = artist_genres[i]
                    genre2 = artist_genres[j]
                    genre_pairs.append((genre1, genre2))
                    genre_pairs.append((genre2, genre1))  # Matrice symétrique
    
    # Convertir les paires en DataFrame pour comptabiliser les occurrences
    df_collaborations = pd.DataFrame(genre_pairs, columns=['Genre1', 'Genre2'])

    # Construire la matrice des collaborations entre genres
    genre_matrix = pd.crosstab(df_collaborations['Genre1'], df_collaborations['Genre2'])
    return genre_matrix