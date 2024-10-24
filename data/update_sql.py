import sqlite3
import pandas as pd
from pymongo import MongoClient
import configparser

config = configparser.ConfigParser()
config.read("./config.ini")

def get_collection_from_db(collection_name):
    client = MongoClient(config['MONGO_DB']['MONGO_URI'])
    db = client[config['MONGO_DB']['DB_NAME']]
    collection = db[collection_name]
    return collection

class UpdateSQLManager:
    def __init__(self):
        self.tracks_collection = get_collection_from_db('tracks')
        self.artists_collection = get_collection_from_db('artists')
        self.albums_collection = get_collection_from_db('albums')
        self.conn = sqlite3.connect('spotify.db')  # Connexion à la base SQL

    def create_sql_tables(self):
        """Crée les tables dans la base SQLite si elles n'existent pas déjà."""
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS artists
                          (id TEXT PRIMARY KEY, name TEXT, popularity INTEGER, followers INTEGER, genres TEXT, market TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tracks
                          (id TEXT PRIMARY KEY, name TEXT, album_id TEXT, tempo REAL, energy REAL, danceability REAL, 
                           acousticness REAL, valence REAL, duration_ms INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS albums
                          (id TEXT PRIMARY KEY, name TEXT, release_date TEXT, available_markets TEXT, total_tracks INTEGER)''')
        self.conn.commit()

    def update_artists(self):
        """Met à jour la table des artistes dans SQLite avec les données de MongoDB."""
        cursor = self.conn.cursor()
        artists = self.artists_collection.find()
        for artist in artists:
            followers = artist.get('followers', {})
            if isinstance(followers, dict):
                followers_total = followers.get('total', 0)
            else:
                followers_total = followers  # Si c'est un entier, on l'utilise directement

            cursor.execute('''INSERT OR REPLACE INTO artists (id, name, popularity, followers, genres, market)
                            VALUES (?, ?, ?, ?, ?, ?)''', 
                        (artist['id'], artist['name'], artist.get('popularity', 0), 
                            followers_total, 
                            ','.join(artist.get('genres', [])), 
                            artist.get('market', '')))
        self.conn.commit()


    def update_tracks(self):
        """Met à jour la table des tracks dans SQLite avec les données de MongoDB."""
        cursor = self.conn.cursor()
        tracks = self.tracks_collection.find()
        for track in tracks:
            cursor.execute('''INSERT OR REPLACE INTO tracks (id, name, album_id, tempo, energy, danceability, acousticness, 
                              valence, duration_ms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (track['id'], track['name'], track['album_id'], track.get('audio_features', {}).get('tempo'),
                            track.get('audio_features', {}).get('energy'), track.get('audio_features', {}).get('danceability'),
                            track.get('audio_features', {}).get('acousticness'), track.get('audio_features', {}).get('valence'),
                            track.get('audio_features', {}).get('duration_ms')))
        self.conn.commit()

    def update_albums(self):
        """Met à jour la table des albums dans SQLite avec les données de MongoDB."""
        cursor = self.conn.cursor()
        albums = self.albums_collection.find()
        for album in albums:
            cursor.execute('''INSERT OR REPLACE INTO albums (id, name, release_date, available_markets, total_tracks) 
                              VALUES (?, ?, ?, ?, ?)''', 
                           (album['id'], album['name'], album.get('release_date'), 
                            ','.join(album.get('available_markets', [])), album.get('total_tracks')))
        self.conn.commit()

    def close_connection(self):
        """Ferme la connexion à la base de données."""
        self.conn.close()

if __name__ == "__main__":
    # Initialisation et création des tables
    manager = UpdateSQLManager()
    manager.create_sql_tables()

    # Mise à jour des tables à partir de MongoDB
    manager.update_artists()
    manager.update_tracks()
    manager.update_albums()

    # Fermeture de la connexion
    manager.close_connection()

    print("Mise à jour de la base SQLite terminée.")
