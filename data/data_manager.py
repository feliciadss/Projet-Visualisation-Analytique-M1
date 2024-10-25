import sqlite3
import pandas as pd
from static.enumerations import genres

class DataManager:
    def __init__(self, db_path='./data/spotify.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    # Fonction pour créer un DataFrame sur les features audios des tracks
    def create_audiofeatures_dataframe(self, selected_genres):
        all_track_data = []

        for genre_selectionné in selected_genres:
            self.cursor.execute("""
                SELECT id FROM artists WHERE genres LIKE ?
            """, (f'%{genre_selectionné}%',))
            artist_ids = [row[0] for row in self.cursor.fetchall()]

            if not artist_ids:
                print(f"Aucun artiste trouvé pour le genre {genre_selectionné}")
                continue

            self.cursor.execute(f"""
                SELECT id, name, tempo, energy, danceability, acousticness, valence, duration_ms
                FROM tracks
                WHERE album_id IN (SELECT id FROM albums WHERE artist_id IN ({','.join('?' for _ in artist_ids)}))
            """, artist_ids)
            tracks = self.cursor.fetchall()

            if not tracks:
                print(f"Aucun track trouvé pour les artistes de {genre_selectionné}")
                continue

            for track in tracks:
                track_info = {
                    'track_id': track[0],
                    'name': track[1],
                    'genre': genre_selectionné,
                    'tempo': track[2],
                    'energy': track[3],
                    'danceability': track[4],
                    'acousticness': track[5],
                    'valence': track[6],
                    'duration_ms': track[7]
                }
                all_track_data.append(track_info)

        df = pd.DataFrame(all_track_data)
        return df
    
    # Fonciton pour créer un dataframe pour récupérer la popularité des artistes et les marchés
    def create_genre_popularity_by_country(self, selected_genre):
        self.cursor.execute("""
            SELECT albums.available_markets, artists.popularity
            FROM albums
            JOIN artists ON albums.artist_id = artists.id
            WHERE artists.genres LIKE ?
        """, (f'%{selected_genre}%',))

        all_album_data = self.cursor.fetchall()
        
        if not all_album_data:
            print(f"Aucun artiste trouvé pour le genre {selected_genre}")
            return pd.DataFrame()

        country_popularity = {}

        for available_markets, artist_popularity in all_album_data:
            markets = available_markets.split(',')
            for market in markets:
                market = market.strip()  
                if market in country_popularity:
                    country_popularity[market] += artist_popularity
                else:
                    country_popularity[market] = artist_popularity

        df = pd.DataFrame(list(country_popularity.items()), columns=['country', 'total_popularity'])

        return df


    # Fonction pour récupérer les sous-genres les plus fréquents pour un genre
    def get_top_subgenres_per_genre(self, genre, top_n=15):
        self.cursor.execute("""
            SELECT genres FROM artists WHERE genres LIKE ?
        """, (f'%{genre}%',))

        all_genres = self.cursor.fetchall()
        subgenres = [genre for sublist in all_genres for genre in sublist[0].split(',')]

        subgenre_counts = pd.Series(subgenres).value_counts().reset_index()
        subgenre_counts.columns = ['subgenre', 'count']
        top_subgenres = subgenre_counts.head(top_n)

        df_subgenres = pd.DataFrame(top_subgenres)
        df_subgenres['genre'] = genre
        return df_subgenres

    # Fonction pour collecter les albums dont les artistes font partie des selected_genres et renvoyer un DataFrame avec la release date
    def create_album_release_dataframe(self, selected_genres):
        all_album_data = []

        for genre_selectionné in selected_genres:
            self.cursor.execute("""
                SELECT albums.id, albums.name, albums.release_date, albums.available_markets
                FROM albums
                JOIN artists ON albums.artist_id = artists.id
                WHERE artists.genres LIKE ?
            """, (f'%{genre_selectionné}%',))
            albums = self.cursor.fetchall()

            if not albums:
                print(f"Aucun album trouvé pour les artistes de {genre_selectionné}")
                continue

            for album in albums:
                album_info = {
                    'album_id': album[0],
                    'album_name': album[1],
                    'release_date': album[2],
                    'genre': genre_selectionné,
                    'available_markets': album[3]
                }
                all_album_data.append(album_info)

        df = pd.DataFrame(all_album_data)
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        return df

    # Fonction pour collecter les collaborations entre genres dans les tracks featurings
    def create_genre_collaboration_matrix(self, selected_genres):
        genre_pairs = []

        for genre_selectionné in selected_genres:
            self.cursor.execute("""
                SELECT DISTINCT artists.id, artists.genres
                FROM artists
                WHERE genres LIKE ?
            """, (f'%{genre_selectionné}%',))
            artist_data = self.cursor.fetchall()

            if not artist_data:
                continue

            for artist_id, artist_genres in artist_data:
                artist_genres_list = artist_genres.split(',')
                for genre in artist_genres_list:
                    for global_genre in genres:
                        if genre.lower().startswith(global_genre.lower()):
                            genre_pairs.append((genre_selectionné, global_genre))
                            break

        if not genre_pairs:
            return pd.DataFrame()

        df_collaborations = pd.DataFrame(genre_pairs, columns=['Genre1', 'Genre2'])
        genre_matrix = pd.crosstab(df_collaborations['Genre1'], df_collaborations['Genre2'])
        return genre_matrix


    def create_genre_count_dataframe(self):
        genre_count = {genre: 0 for genre in genres}  

        self.cursor.execute("""
            SELECT artists.genres, COUNT(albums.id)
            FROM artists
            JOIN albums ON artists.id = albums.artist_id
            GROUP BY artists.genres
        """)

        artist_genres = self.cursor.fetchall()

        for genres_in_db, album_count in artist_genres:
            genre_list = genres_in_db.split(',') 
            for genre in genre_list:
                genre = genre.strip().lower()
                for global_genre in genres:
                    if genre.startswith(global_genre):
                        genre_count[global_genre] += album_count  
                        break

        df_genre_count = pd.DataFrame(list(genre_count.items()), columns=['genre', 'total_count'])

        return df_genre_count


    def close_connection(self):
        """Ferme la connexion à la base de données."""
        self.conn.close()
