import requests
from pymongo import MongoClient
from auth_spotify import spotify_auth
from itertools import combinations
import configparser

config = configparser.ConfigParser()
config.read("C:/Users/PC/OneDrive/Documents/projet-visualisation-analytique-m1/data/config.ini")

BASE_URL = "https://api.spotify.com/v1/"
# Connexion MongoDB
def connect_to_db():
    client = MongoClient(config['MONGO_DB']['MONGO_URI'])
    db = client[config['MONGO_DB']['DB_NAME']]
    return db

# Récupération des 50 artistes d'un genre musical spécifique dans un marché donné
def get_genre_artists(genre, market, limit=50):
    token = spotify_auth.get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": f"genre:{genre}",
        "type": "artist",
        "market": market,
        "limit": min(limit, 50)  # Limite à 50 par requête, pagination nécessaire
    }
    
    artists = []
    while len(artists) < limit:
        response = requests.get(f"{BASE_URL}search", headers=headers, params=params)
        if response.status_code == 200:
            new_artists = response.json()["artists"]["items"]
            artists.extend(new_artists)
            if len(new_artists) < 50:
                break  # Stop si moins de 50 artistes
        else:
            raise Exception(f"Failed to get artists for genre {genre} in {market}")
    
    return artists[:limit]  # Retourner les 50 premiers

# Sauvegarde MongoDB des artistes
def save_artists_to_db(artists, genre, market, db):
    collection = db["artists"]
    genre_collection = db["genres"]
    market_collection = db["markets"]

    # Enregistrer les genres et les marchés
    genre_collection.update_one({"name": genre}, {"$set": {"name": genre}}, upsert=True)
    market_collection.update_one({"name": market}, {"$set": {"name": market}}, upsert=True)

    for artist in artists:
        artist["genre"] = genre  # Associer le genre à l'artiste
        artist["market"] = market  # Associer le marché à l'artiste
        collection.update_one(
            {"id": artist["id"]}, 
            {"$set": artist}, 
            upsert=True
        )

# Récupérer les albums par genre et marché
def get_genre_albums(genre, market, limit=20):
    token = spotify_auth.get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": f"genre:{genre}",
        "type": "album",
        "market": market,
        "limit": min(limit, 50)
    }
    
    albums = []
    while len(albums) < limit:
        response = requests.get(f"{BASE_URL}search", headers=headers, params=params)
        if response.status_code == 200:
            new_albums = response.json()["albums"]["items"]
            albums.extend(new_albums)
            if len(new_albums) < 50:
                break  
        else:
            raise Exception(f"Failed to get albums for genre {genre} in {market}")
    
    return albums[:limit]  # Retourner les albums

# Sauvegarde MongoDB des albums
def save_albums_to_db(albums, genre, market, db):
    collection = db["albums"]
    genre_collection = db["genres"]
    market_collection = db["markets"]

    # Enregistrer les genres et les marchés
    genre_collection.update_one({"name": genre}, {"$set": {"name": genre}}, upsert=True)
    market_collection.update_one({"name": market}, {"$set": {"name": market}}, upsert=True)

    for album in albums:
        album["genre"] = genre  # Associer le genre à l'album
        album["market"] = market  # Associer le marché à l'album
        collection.update_one(
            {"id": album["id"]}, 
            {"$set": album}, 
            upsert=True
        )

# Récupérer les morceaux d'un album
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

# Sauvegarde MongoDB des morceaux
def save_tracks_to_db(tracks, album_id, db):
    collection = db["tracks"]
    for track in tracks:
        track["album_id"] = album_id  # Associer l'album au morceau
        collection.update_one(
            {"id": track["id"]},
            {"$set": track},
            upsert=True
        )

# Récupération des 10 playlists les plus populaires d'un marché
def get_popular_playlists(market, limit=10):
    token = spotify_auth.get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "country": market,
        "limit": min(limit, 30)
    }
    response = requests.get(f"{BASE_URL}browse/featured-playlists", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["playlists"]["items"][:limit]
    else:
        raise Exception(f"Failed to get playlists for market {market}")

# Sauvegarde MongoDB des playlists
def save_playlists_to_db(playlists, market, db):
    collection = db["playlists"]
    for playlist in playlists:
        playlist["market"] = market  # Associer le marché à la playlist
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
