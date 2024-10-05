import requests
from pymongo import MongoClient, UpdateOne
from auth_spotify import spotify_auth
import configparser
import time

config = configparser.ConfigParser()
config.read("C:/Users/PC/OneDrive/Documents/projet-visualisation-analytique-m1/data/config.ini")

BASE_URL = "https://api.spotify.com/v1/"

# Connexion à MongoDB
def connect_to_db():
    client = MongoClient(config['MONGO_DB']['MONGO_URI'])
    db = client[config['MONGO_DB']['DB_NAME']]
    return db

# Gestion des limitations d'API (limitation de requêtes)
def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 5))
        print(f"Rate limit hit. Retrying after {retry_after} seconds.")
        time.sleep(retry_after)


# Récupérer les playlists populaires pour un pays
def get_popular_playlists(country, limit=20):
    token = spotify_auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "market": country,
        "limit": limit
    }
    response = requests.get(f"{BASE_URL}browse/featured-playlists", headers=headers, params=params)
    
    if response.status_code == 429:
        handle_rate_limit(response)
        return get_popular_playlists(country, limit)  # Réessayer après délai
    elif response.status_code == 200:
        return response.json()["playlists"]["items"]
    else:
        raise Exception(f"Failed to get playlists for country {country}")

# Récupérer les tracks d'une playlist
def get_playlist_tracks(playlist_id):
    token = spotify_auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}playlists/{playlist_id}/tracks", headers=headers)
    
    if response.status_code == 429:
        handle_rate_limit(response)
        return get_playlist_tracks(playlist_id)
    elif response.status_code == 200:
        return response.json()["items"]
    else:
        raise Exception(f"Failed to get tracks for playlist {playlist_id}")

# Récupérer les albums populaires par pays
def get_popular_albums(country, limit=50):
    token = spotify_auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "market": country,
        "limit": limit
    }
    response = requests.get(f"{BASE_URL}browse/new-releases", headers=headers, params=params)
    
    if response.status_code == 429:
        handle_rate_limit(response)
        return get_popular_albums(country, limit)  # Réessayer après délai
    elif response.status_code == 200:
        return response.json()["albums"]["items"]
    else:
        raise Exception(f"Failed to get albums for country {country}")

# Sauvegarder un album à la fois dans MongoDB avec gestion du champ 'top_market'
def save_album_to_db(album, country, db):
    collection = db["albums"]
    album_id = album["id"]
    
    # Rechercher l'album existant dans la base de données
    existing_album = collection.find_one({"id": album_id})
    
    # Si l'album existe déjà, récupérer sa liste de marchés
    if existing_album:
        top_market_list = existing_album.get("top_market", [])
        
        # Si le marché n'est pas déjà dans la liste, l'ajouter
        if country not in top_market_list:
            top_market_list.append(country)
    else:
        # Si l'album n'existe pas encore, créer une nouvelle liste de marchés
        top_market_list = [country]

    # Mettre à jour le document de l'album avec la liste mise à jour des marchés
    album["top_market"] = top_market_list

    # Sauvegarder ou mettre à jour l'album dans MongoDB
    collection.update_one({"id": album_id}, {"$set": album}, upsert=True)

# Récupérer les morceaux d'un album
def get_album_tracks(album_id):
    token = spotify_auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}albums/{album_id}/tracks", headers=headers)
    
    if response.status_code == 429:
        handle_rate_limit(response)
        return get_album_tracks(album_id)  # Réessayer après délai
    elif response.status_code == 200:
        return response.json()["items"]
    else:
        raise Exception(f"Failed to get tracks for album {album_id}")

# Sauvegarder un morceau à la fois dans MongoDB avec gestion des informations manquantes
def save_track_to_db(track, album_id, db):
    collection = db["tracks"]
    track["album_id"] = album_id
    audio_features = get_audio_features([track["id"]])

    if audio_features:
        track["audio_features"] = {
            "tempo": audio_features.get("tempo", None),
            "energy": audio_features.get("energy", None),
            "danceability": audio_features.get("danceability", None),
            "acousticness": audio_features.get("acousticness", None),
            "valence": audio_features.get("valence", None),
            "duration_ms": audio_features.get("duration_ms", None)
        }

    collection.update_one({"id": track["id"]}, {"$set": track}, upsert=True)

# Récupérer les caractéristiques audio d'un morceau
def get_audio_features(track_ids):
    token = spotify_auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}audio-features", headers=headers, params={"ids": ",".join(track_ids)})
    
    if response.status_code == 429:
        handle_rate_limit(response)
        return get_audio_features(track_ids)  # Réessayer après délai
    elif response.status_code == 200:
        features = response.json()["audio_features"]
        return features[0] if features else None
    else:
        raise Exception(f"Failed to get audio features for tracks {track_ids}")

# Récupérer les informations d'un artiste
def get_artist_info(artist_id):
    token = spotify_auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}artists/{artist_id}", headers=headers)

    if response.status_code == 429:
        handle_rate_limit(response)
        return get_artist_info(artist_id)  # Réessayer après délai
    elif response.status_code == 200:
        artist_data = response.json()
        return {
            "id": artist_data["id"],
            "name": artist_data["name"],
            "popularity": artist_data.get("popularity", None),
            "followers": artist_data["followers"]["total"],
            "genres": artist_data["genres"],
            "country": artist_data.get("country", "Unknown")
        }
    else:
        raise Exception(f"Failed to get artist info for {artist_id}")

# Sauvegarder un artiste à la fois dans MongoDB
def save_artist_to_db(artist, db):
    collection = db["artists"]
    collection.update_one({"id": artist["id"]}, {"$set": artist}, upsert=True)
