import requests
from pymongo import MongoClient
from auth_spotify import spotify_auth
import configparser

config = configparser.ConfigParser()
config.read("C:/Users/PC/OneDrive/Documents/projet-visualisation-analytique-m1/data/config.ini")

BASE_URL = "https://api.spotify.com/v1/"

# Connexion MongoDB
def connect_to_db():
    client = MongoClient(config['MONGO_DB']['MONGO_URI'])
    db = client[config['MONGO_DB']['DB_NAME']]
    return db

# Récupérer les albums par genre et marché
def get_genre_albums(genre, market, limit=50):
    token = spotify_auth.get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": f"genre:{genre}",
        "type": "album",
        "market": market,
        "limit": min(limit, 50),
        "sort": "popularity"  #tri par popularité
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
    
    return albums[:limit]

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
def get_album_tracks(album_id, limit=20):
    token = spotify_auth.get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(f"{BASE_URL}albums/{album_id}/tracks", headers=headers)
    if response.status_code == 200:
        tracks = response.json()["items"]
        return tracks[:limit]  # Limiter à 15 morceaux maximum
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

# Récupérer les artistes associés aux morceaux
def get_artists_from_tracks(tracks): 
    artists = set()
    for track in tracks:
        for artist in track["artists"]:
            artists.add(artist["id"])
    return list(artists)

# Sauvegarde MongoDB des artistes
def save_artists_to_db(artists, genre, market, db):
    collection = db["artists"]
    genre_collection = db["genres"]
    market_collection = db["markets"]

    # Enregistrer les genres et les marchés
    genre_collection.update_one({"name": genre}, {"$set": {"name": genre}}, upsert=True)
    market_collection.update_one({"name": market}, {"$set": {"name": market}}, upsert=True)

    for artist in artists:
        artist_data = {
            "id": artist,
            "genre": genre,
            "market": market
        }
        collection.update_one(
            {"id": artist}, 
            {"$set": artist_data}, 
            upsert=True
        )
