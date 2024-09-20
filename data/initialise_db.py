# initialise_db.py

from constructeurDB import get_genre_artists, save_artists_to_db, get_genre_albums, save_albums_to_db, connect_to_db

def initialize_db():
    db = connect_to_db()
    genres = ["pop", "rock", "hip-hop", "jazz"]  # Genres à récupérer
    european_countries = ["FR", "DE", "ES", "IT", "GB"]  # Liste des marchés européens

    for genre in genres:
        for market in european_countries:
            # Récupérer et stocker les artistes
            print(f"Fetching artists for genre {genre} in market {market}...")
            artists = get_genre_artists(genre, market)
            save_artists_to_db(artists, db)
            
            # Récupérer et stocker les albums
            print(f"Fetching albums for genre {genre} in market {market}...")
            albums = get_genre_albums(genre, market)
            save_albums_to_db(albums, db)

if __name__ == "__main__":
    initialize_db()
