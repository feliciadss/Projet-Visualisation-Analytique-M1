# constructeur_db.py

import requests
from pymongo import MongoClient
from auth_spotify import spotify_auth
import config

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
        "limit": 50  # Limite à 50 artistes par requête
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
