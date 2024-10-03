import requests
from pymongo import MongoClient
from auth_spotify import spotify_auth
import configparser

config = configparser.ConfigParser()
config.read("C:/Users/PC/OneDrive/Documents/projet-visualisation-analytique-m1/data/config.ini")

BASE_URL = "https://api.spotify.com/v1/"

# Connexion à MongoDB
def connect_to_db():
    client = MongoClient(config['MONGO_DB']['MONGO_URI'])
    db = client[config['MONGO_DB']['DB_NAME']]
    return db

# Récupérer les albums par genre et marché
def get_genre_albums(genre, market, limit=50):
    token = spotify_auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": f"genre:{genre}",
        "type": "album",
        "market": market,
        "limit": min(limit, 50),
        "sort": "popularity"
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

# Sauvegarder les albums dans MongoDB
def save_albums_to_db(albums, genre, market, db):
    collection = db["albums"]
    genre_collection = db["genres"]
    market_collection = db["markets"]

    genre_collection.update_one({"name": genre}, {"$set": {"name": genre}}, upsert=True)
    market_collection.update_one({"name": market}, {"$set": {"name": market}}, upsert=True)

    for album in albums:
        album["genre"] = genre
        album["market"] = market
        collection.update_one({"id": album["id"]}, {"$set": album}, upsert=True)

# Récupérer les morceaux d'un album
def get_album_tracks(album_id, limit=20):
    token = spotify_auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}albums/{album_id}/tracks", headers=headers)
    if response.status_code == 200:
        return response.json()["items"][:limit]
    else:
        raise Exception(f"Failed to get tracks for album {album_id}")

# Récupérer les caractéristiques audio des morceaux
def get_audio_features(track_ids):
    token = spotify_auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}audio-features", headers=headers, params={"ids": ",".join(track_ids)})
    if response.status_code == 200:
        return response.json()["audio_features"]
    else:
        raise Exception(f"Failed to get audio features for tracks {track_ids}")

# Sauvegarder les morceaux dans MongoDB
def save_tracks_to_db(tracks, album_id, db):
    collection = db["tracks"]
    track_ids = [track["id"] for track in tracks]
    audio_features = get_audio_features(track_ids)

    for track, features in zip(tracks, audio_features):
        if features:
            existing_track = collection.find_one({"id": track["id"]})
            if not existing_track:
                track["album_id"] = album_id
                track["audio_features"] = {
                    "tempo": features["tempo"],
                    "energy": features["energy"],
                    "danceability": features["danceability"],
                    "acousticness": features["acousticness"],
                    "valence": features["valence"],
                    "duration_ms": features["duration_ms"]
                }
                collection.update_one({"id": track["id"]}, {"$set": track}, upsert=True)
            else:
                print(f"Track {track['name']} already exists in the database.")

# Récupérer les informations des artistes associés aux morceaux
def get_artists_from_tracks(tracks):
    artists_data = []
    for track in tracks:
        for artist in track["artists"]:
            artist_info = get_artist_info(artist["id"])
            if artist_info:
                artists_data.append(artist_info)
    return artists_data

# Récupérer les informations d'un artiste
def get_artist_info(artist_id):
    token = spotify_auth.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}artists/{artist_id}", headers=headers)

    if response.status_code == 200:
        artist_data = response.json()
        return {
            "id": artist_data["id"],
            "name": artist_data["name"],
            "popularity": artist_data["popularity"],
            "followers": artist_data["followers"]["total"],
            "genres": artist_data["genres"],
            "country": artist_data.get("country", "Unknown")
        }
    else:
        raise Exception(f"Failed to get artist info for {artist_id}")

# Sauvegarder les artistes dans MongoDB
def save_artists_to_db(artists, genre, market, db):
    collection = db["artists"]
    genre_collection = db["genres"]
    market_collection = db["markets"]

    genre_collection.update_one({"name": genre}, {"$set": {"name": genre}}, upsert=True)
    market_collection.update_one({"name": market}, {"$set": {"name": market}}, upsert=True)

    for artist in artists:
        existing_artist = collection.find_one({"id": artist["id"]})
        if not existing_artist:
            artist_data = {
                "id": artist["id"],
                "name": artist.get("name"),
                "popularity": artist["popularity"],
                "followers": artist["followers"],
                "country": artist["country"],
                "genre": genre,
                "market": market
            }
            collection.update_one({"id": artist["id"]}, {"$set": artist_data}, upsert=True)
        else:
            print(f"Artist {artist['name']} already exists in the database.")