import sqlite3
import pandas as pd
from pymongo import MongoClient
import configparser
import os

db_path = os.path.join(os.path.dirname(__file__), 'spotify.db')

config = configparser.ConfigParser()
config.read("./config.ini")

def get_collection_from_db(collection_name):
    try:
        if 'MONGO_DB' not in config or 'MONGO_URI' not in config['MONGO_DB'] or 'DB_NAME' not in config['MONGO_DB']:
            raise ValueError("Allez dans le dossier 'data', fichier 'config.ini', et entrez vos identifiants MongoDB et Spotify Developer.")
        client = MongoClient(config['MONGO_DB']['MONGO_URI'])
        db = client[config['MONGO_DB']['DB_NAME']]

    except Exception as e:
        raise ValueError("Allez dans le dossier 'data', fichier 'config.ini', et entrez vos identifiants MongoDB et Spotify Developer.") from e
    
    collection = db[collection_name]
    return collection

class UpdateSQLManager:
    def __init__(self):
        self.tracks_collection = get_collection_from_db('tracks')
        self.artists_collection = get_collection_from_db('artists')
        self.albums_collection = get_collection_from_db('albums')
        self.conn = sqlite3.connect(db_path)

    def create_sql_tables(self):
        """Crée les tables dans la base SQLite si elles n'existent pas déjà."""
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS artists
                                (id TEXT PRIMARY KEY, name TEXT, popularity INTEGER, followers INTEGER, genres TEXT, market TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tracks
                                (id TEXT PRIMARY KEY, name TEXT, album_id TEXT, tempo REAL, energy REAL, danceability REAL, 
                                acousticness REAL, valence REAL, duration_ms INTEGER, preview_url TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS albums
                                (id TEXT PRIMARY KEY, name TEXT, release_date TEXT, available_markets TEXT, total_tracks INTEGER, artist_id TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS track_artists
                                (track_id TEXT, artist_id TEXT, 
                                FOREIGN KEY (track_id) REFERENCES tracks(id), 
                                FOREIGN KEY (artist_id) REFERENCES artists(id),
                                PRIMARY KEY (track_id, artist_id))''')
        self.conn.commit()


    def update_artists(self):
        """Met à jour la table des artistes dans SQLite avec les données de MongoDB."""
        cursor = self.conn.cursor()
        artists = self.artists_collection.find()
        for artist in artists:
            followers = artist.get('followers', {})
            followers_total = followers.get('total', 0) if isinstance(followers, dict) else followers

            cursor.execute('''INSERT OR REPLACE INTO artists (id, name, popularity, followers, genres, market)
                            VALUES (?, ?, ?, ?, ?, ?)''', 
                        (artist['id'], artist.get('name', ''), artist.get('popularity', 0), 
                         followers_total, 
                         ','.join(artist.get('genres', [])), 
                         artist.get('market', '')))
        self.conn.commit()

    def update_tracks(self):
        """Met à jour la table des tracks dans SQLite avec les données de MongoDB."""
        cursor = self.conn.cursor()
        tracks = self.tracks_collection.find()
        for track in tracks:
            audio_features = track.get('audio_features', {})
            cursor.execute('''INSERT OR REPLACE INTO tracks (id, name, album_id, tempo, energy, danceability, acousticness, 
                              valence, duration_ms, preview_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (track['id'], track.get('name', ''), track.get('album_id', ''),
                            audio_features.get('tempo'), audio_features.get('energy'),
                            audio_features.get('danceability'), audio_features.get('acousticness'),
                            audio_features.get('valence'), audio_features.get('duration_ms'), track.get('preview_url','')))
            # Insérer les associations artiste-morceau dans la table track_artists
            artists = track.get('artists', [])
            for artist in artists:
                cursor.execute('''INSERT OR REPLACE INTO track_artists (track_id, artist_id) 
                                VALUES (?, ?)''', (track['id'], artist['id']))
        self.conn.commit()

    def update_albums(self):
        """Met à jour la table des albums dans SQLite avec les données de MongoDB."""
        cursor = self.conn.cursor()
        albums = self.albums_collection.find()
        for album in albums:
            artists = album.get('artists', [])
            artist_id = artists[0]['id'] if artists else None

            cursor.execute('''INSERT OR REPLACE INTO albums (id, name, release_date, available_markets, total_tracks, artist_id) 
                              VALUES (?, ?, ?, ?, ?, ?)''', 
                           (album['id'], album.get('name', ''), album.get('release_date', ''),
                            ','.join(album.get('available_markets', [])), album.get('total_tracks', 0),
                            artist_id))  
        self.conn.commit()
        
    def add_preview_url_column_if_not_exists(self):
        """Vérifie si la colonne preview_url existe dans la table tracks et l'ajoute si nécessaire."""
        cursor = self.conn.cursor()
        
        cursor.execute("PRAGMA table_info(tracks)")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        
        if 'preview_url' not in column_names:
            cursor.execute("ALTER TABLE tracks ADD COLUMN preview_url TEXT")
            self.conn.commit()
            print("Colonne preview_url ajoutée à la table tracks.")
        else:
            print("La colonne preview_url existe déjà.")

                
            
    def add_artist_id_column_if_not_exists(self):  
        """Vérifie si la colonne artist_id existe dans la table albums et l'ajoute si nécessaire."""
        cursor = self.conn.cursor()
        
        cursor.execute("PRAGMA table_info(albums)")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        
        if 'artist_id' not in column_names:
            cursor.execute("ALTER TABLE albums ADD COLUMN artist_id TEXT")
            self.conn.commit()
            print("Colonne artist_id ajoutée à la table albums.")
        else:
            print("La colonne artist_id existe déjà.")


    def close_connection(self):
        """Ferme la connexion à la base de données."""
        self.conn.close()
        
if __name__ == "__main__":
    manager = UpdateSQLManager()
    manager.create_sql_tables()
    
    manager.add_artist_id_column_if_not_exists()
    manager.update_artists()
    manager.add_preview_url_column_if_not_exists()
    manager.update_tracks()
    manager.update_albums()

    manager.close_connection()

    print("Mise à jour de la base SQLite terminée.")
