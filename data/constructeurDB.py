import requests
from pymongo import MongoClient
from auth_spotify import spotify_auth
import configparser
from itertools import combinations

config = configparser.ConfigParser()
config.read("data/config.ini")

BASE_URL = "https://api.spotify.com/v1/"

# Connexion à MongoDB
def connect_to_db():
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    return db

# Récupération des artistes d'un genre musical spécifique dans un marché donné
def get_genre_artists(genre, market):
    token = spotify_auth.get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": f"genre:{genre}",
        "type": "artist",
        "market": market,
        "limit": 50  # Limite à 50 artistes/ requête
    }
    response = requests.get(f"{BASE_URL}search", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["artists"]["items"]
    else:
        raise Exception(f"Failed to get artists for genre {genre} in {market}")

# Sauvegarder les artistes dans MongoDB
def save_artists_to_db(artists, db):
    collection = db["artists"]
    for artist in artists:
        collection.update_one(
            {"id": artist["id"]}, 
            {"$set": artist}, 
            upsert=True
        )

# Récupération des albums d'un genre musical spécifique dans un marché donné
def get_genre_albums(genre, market):
    token = spotify_auth.get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": f"genre:{genre}",
        "type": "album",
        "market": market,
        "limit": 50
    }
    response = requests.get(f"{BASE_URL}search", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["albums"]["items"]
    else:
        raise Exception(f"Failed to get albums for genre {genre} in {market}")

# Sauvegarder les albums dans MongoDB
def save_albums_to_db(albums, db):
    collection = db["albums"]
    for album in albums:
        collection.update_one(
            {"id": album["id"]}, 
            {"$set": album}, 
            upsert=True
        )

# Récupération des morceaux d'un album
def get_album_tracks(album_id):
    token = spotify_auth.get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(f"{BASE_URL}albums/{album_id}/tracks", headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        raise Exception(f"Failed to get tracks for album {album_id}")

# Sauvegarder les morceaux dans MongoDB
def save_tracks_to_db(tracks, db):
    collection = db["tracks"]
    for track in tracks:
        collection.update_one(
            {"id": track["id"]},
            {"$set": track},
            upsert=True
        )

# Récupération des playlists populaires
def get_popular_playlists(market, limit=50):
    token = spotify_auth.get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "country": market,
        "limit": limit
    }
    response = requests.get(f"{BASE_URL}browse/featured-playlists", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["playlists"]["items"]
    else:
        raise Exception(f"Failed to get playlists for market {market}")
    
# Sauvegarder les playlists dans MongoDB
def save_playlists_to_db(playlists, db):
    collection = db["playlists"]
    for playlist in playlists:
        collection.update_one(
            {"id": playlist["id"]},
            {"$set": playlist},
            upsert=True
        )

# Récupération des caractéristiques audio des morceaux
def get_audio_features(track_ids):
    token = spotify_auth.get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "ids": ",".join(track_ids)
    }
    response = requests.get(f"{BASE_URL}audio-features", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["audio_features"]
    else:
        raise Exception("Failed to get audio features")
    
# Sauvegarder les caractéristiques audio dans MongoDB
def save_audio_features_to_db(audio_features, db):
    collection = db["audio_features"]
    for feature in audio_features:
        if feature:  # Vérifie si les caractéristiques existent
            collection.update_one(
                {"id": feature["id"]},
                {"$set": feature},
                upsert=True
            )

# Analyser et sauvegarder les collaborations
def analyze_and_save_collaborations(playlists, db):
    collaboration_counts = {}
    for playlist in playlists:
        # Supposons que chaque playlist contient une liste de morceaux avec artistes
        tracks = playlist.get("tracks", {}).get("items", [])
        artists_in_playlist = set()
        for item in tracks:
            track = item.get("track", {})
            for artist in track.get("artists", []):
                artists_in_playlist.add(artist["id"])
        
        # Générer toutes les paires possibles d'artistes dans la playlist
        for pair in combinations(artists_in_playlist, 2):
            sorted_pair = tuple(sorted(pair))
            collaboration_counts[sorted_pair] = collaboration_counts.get(sorted_pair, 0) + 1
    
    # Sauvegarder les collaborations dans MongoDB
    collection = db["collaborations"]
    for pair, count in collaboration_counts.items():
        collection.update_one(
            {"artists": pair},
            {"$set": {"count": count}},
            upsert=True
        )
