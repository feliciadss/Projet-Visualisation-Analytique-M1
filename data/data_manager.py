import sqlite3
import pandas as pd

class DataManager:
    def __init__(self, db_path='./spotify.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    # Fonction pour créer un DataFrame sur les features audios des tracks
    def create_audiofeatures_dataframe(self, selected_genres):
        all_track_data = []

        for genre_selectionné in selected_genres:
            # Requête SQL pour trouver les artistes correspondant au genre sélectionné
            self.cursor.execute("""
                SELECT id FROM artists WHERE genres LIKE ?
            """, (f'%{genre_selectionné}%',))
            artist_ids = [row[0] for row in self.cursor.fetchall()]

            if not artist_ids:
                print(f"Aucun artiste trouvé pour le genre {genre_selectionné}")
                continue

            # Requête SQL pour trouver les tracks des artistes
            self.cursor.execute(f"""
                SELECT id, name, tempo, energy, danceability, acousticness, valence, duration_ms
                FROM tracks
                WHERE album_id IN (SELECT id FROM albums WHERE artists IN ({','.join('?' for _ in artist_ids)}))
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

    # Fonction pour créer un DataFrame avec la popularité des genres par pays
    def create_album_top_market_dataframe(self, selected_genre):
        self.cursor.execute("""
            SELECT albums.id, albums.name, albums.top_market
            FROM albums
            JOIN artists ON albums.artists = artists.id
            WHERE artists.genres LIKE ?
        """, (f'%{selected_genre}%',))

        all_album_data = self.cursor.fetchall()
        if not all_album_data:
            print(f"Aucun album trouvé pour le genre {selected_genre}")
            return pd.DataFrame()

        df = pd.DataFrame(all_album_data, columns=['album_id', 'album_name', 'market'])
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
                JOIN artists ON albums.artists = artists.id
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
        global_genres = [
            "pop", "rock", "latin", "jazz", "classical",
            "electronic", "indie", "reggae", "blues", "metal",
            "folk", "country", "r&b", "soul"
        ]

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
                    for global_genre in global_genres:
                        if genre.lower().startswith(global_genre.lower()):
                            genre_pairs.append((genre_selectionné, global_genre))
                            break

        if not genre_pairs:
            return pd.DataFrame()

        df_collaborations = pd.DataFrame(genre_pairs, columns=['Genre1', 'Genre2'])
        genre_matrix = pd.crosstab(df_collaborations['Genre1'], df_collaborations['Genre2'])
        return genre_matrix

    def close_connection(self):
        """Ferme la connexion à la base de données."""
        self.conn.close()
